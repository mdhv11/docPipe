import json
import os
import uuid
from typing import List
from tempfile import TemporaryDirectory
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, FileResponse

from app.llm.llama_runner import LlamaCppClient
from app.ocr.paddle import PaddleOcrExtractor
from app.preprocess.image_cleaner import ImageCleaner
from app.renderers.docx_renderer import DocxRenderer
from app.routing.classifier import DocumentRouter
from app.schemas.document_schema import DocumentParseResult
from app.utils.paths import DATA_DIR, OUTPUT_DIR, UPLOAD_DIR
from app.utils.batch_store import create_batch, get_batch_status, get_batch_results, update_batch_status
from app.utils.status_store import write_status, read_status
from app.utils.retry_utils import retry_with_backoff, retry_batch_operation

router = APIRouter()

from dotenv import load_dotenv

load_dotenv()

ocr_extractor = PaddleOcrExtractor()
image_cleaner = ImageCleaner()
docx_renderer = DocxRenderer()
llama = LlamaCppClient(
    binary_path=os.getenv("LLAMA_CPP_BIN", "/usr/local/bin/llama"),
    model_path=os.getenv("LLAMA_CPP_MODEL", "/models/llama-2-7b.gguf"),
)
@retry_with_backoff(max_retries=2, initial_delay=1.0, retry_on=(OSError, RuntimeError))
def extract_text_with_retry(ocr_extractor, image_path: Path) -> str:
    return ocr_extractor.extract_text(image_path)


@retry_with_backoff(max_retries=2, initial_delay=2.0, retry_on=(OSError, RuntimeError))
def run_llm_with_retry(llama_client, prompt: str) -> str:
    return llama_client.run(prompt)

@router.post("/upload")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    document_id = uuid.uuid4().hex
    upload_path = UPLOAD_DIR / f"{document_id}_{file.filename}"

    contents = await file.read()
    upload_path.write_bytes(contents)

    route = DocumentRouter.classify(upload_path)
    write_status(
        document_id,
        status="processing",
        current_task="queued",
        total_pages=None,
        processed_pages=0,
    )

    background_tasks.add_task(process_document_with_retry, document_id, upload_path, file.filename, route)
    return {"document_id": document_id, "status": "processing"}


@router.post("/upload/batch")
async def upload_batch(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    document_ids = []

    for file in files:
        document_id = uuid.uuid4().hex
        upload_path = UPLOAD_DIR / f"{document_id}_{file.filename}"

        contents = await file.read()
        upload_path.write_bytes(contents)

        route = DocumentRouter.classify(upload_path)
        write_status(
            document_id,
            status="processing",
            current_task="queued",
            total_pages=None,
            processed_pages=0,
        )

        document_ids.append(document_id)

        # Start processing each document
        background_tasks.add_task(process_document_with_retry, document_id, upload_path, file.filename, route)

    # Create batch tracking
    batch_id = create_batch(document_ids)
    background_tasks.add_task(monitor_batch_completion, batch_id, document_ids)

    return {
        "batch_id": batch_id,
        "document_ids": document_ids,
        "total_files": len(document_ids),
        "status": "processing"
    }


def monitor_batch_completion(batch_id: str, document_ids: List[str]) -> None:
    """Monitor batch completion and update batch status."""
    import time

    max_wait_time = 3600  # 1 hour timeout
    check_interval = 5  # Check every 5 seconds
    elapsed = 0

    while elapsed < max_wait_time:
        results = get_batch_results(batch_id)
        completed = sum(1 for r in results if r["status"] in ["completed", "failed"])

        if completed == len(document_ids):
            # All documents are done
            errors = [r["error"] for r in results if r["status"] == "failed" and r.get("error")]
            if errors:
                update_batch_status(batch_id, "completed_with_errors", errors)
            else:
                update_batch_status(batch_id, "completed")
            return

        time.sleep(check_interval)
        elapsed += check_interval

    # Timeout - mark as failed
    update_batch_status(batch_id, "failed", ["Batch processing timed out"])


@retry_with_backoff(max_retries=2, initial_delay=2.0, retry_on=(OSError, RuntimeError))
def process_document_with_retry(document_id: str, upload_path: Path, filename: str, route: str) -> None:
    """Wrapper for process_document with retry logic."""
    return process_document(document_id, upload_path, filename, route)


def process_document(document_id: str, upload_path: Path, filename: str, route: str) -> None:
    total_pages = None
    processed_pages = None

    try:
        if route == "image":
            write_status(document_id, status="processing", current_task="analyzing image type")
            write_status(document_id, status="processing", current_task="preprocessing image")
            cleaned_path = image_cleaner.clean(upload_path)
            write_status(document_id, status="processing", current_task="running OCR on image")
            ocr_text = extract_text_with_retry(ocr_extractor, cleaned_path)
        elif route == "pdf":
            write_status(document_id, status="processing", current_task="analyzing PDF structure")
            write_status(document_id, status="processing", current_task="converting PDF to images")
            with TemporaryDirectory() as temp_dir:
                page_files = ocr_extractor.convert_pdf_to_images(upload_path, temp_dir)
                total_pages = len(page_files)
                write_status(
                    document_id,
                    status="processing",
                    current_task="starting OCR on PDF pages",
                    total_pages=total_pages,
                    processed_pages=0,
                )

                page_texts = []
                for index, page_file in enumerate(page_files, start=1):
                    write_status(
                        document_id,
                        status="processing",
                        current_task=f"running OCR on page {index}/{total_pages}",
                        total_pages=total_pages,
                        processed_pages=index - 1,
                    )
                    page_texts.append(extract_text_with_retry(ocr_extractor, page_file))
                    processed_pages = index
                    write_status(
                        document_id,
                        status="processing",
                        current_task=f"completed OCR on page {index}/{total_pages}",
                        total_pages=total_pages,
                        processed_pages=processed_pages,
                    )

                ocr_text = "\n\n".join(page_texts)

        else:
            write_status(document_id, status="processing", current_task="analyzing file type")
            write_status(document_id, status="processing", current_task="running OCR")
            ocr_text = ocr_extractor.extract_text(upload_path)

        write_status(document_id, status="processing", current_task="preparing document reconstruction prompt")
        prompt = llama.build_document_prompt(ocr_text, filename)
        write_status(document_id, status="processing", current_task="running llama.cpp inference")
        llm_response = run_llm_with_retry(llama, prompt)
        write_status(document_id, status="processing", current_task="parsing LLM response")

        try:
            parsed = json.loads(llm_response)
        except json.JSONDecodeError as exc:
            raise RuntimeError("llama.cpp response was not valid JSON") from exc

        write_status(document_id, status="processing", current_task="validating document structure")
        document = DocumentParseResult.parse_obj(parsed)
        write_status(document_id, status="processing", current_task="saving processed document")
        output_path = DATA_DIR / f"{document_id}.json"
        output_path.write_text(document.json(indent=2, ensure_ascii=False), encoding="utf-8")

        write_status(
            document_id,
            status="completed",
            current_task="document processing complete",
            total_pages=total_pages,
            processed_pages=processed_pages,
        )

    except Exception as exc:
        write_status(
            document_id,
            status="failed",
            current_task="error occurred during processing",
            error=str(exc),
        )


@router.get("/batch/{batch_id}")
def get_batch_info(batch_id: str):
    try:
        batch_data = get_batch_status(batch_id)
        results = get_batch_results(batch_id)

        # Calculate summary stats
        total = len(results)
        completed = sum(1 for r in results if r["status"] == "completed")
        failed = sum(1 for r in results if r["status"] == "failed")
        processing = sum(1 for r in results if r["status"] == "processing")

        return {
            **batch_data,
            "summary": {
                "total": total,
                "completed": completed,
                "failed": failed,
                "processing": processing,
                "success_rate": completed / total if total > 0 else 0,
            },
            "results": results,
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Batch not found")


@router.get("/batch/{batch_id}/results")
def get_batch_results_endpoint(batch_id: str):
    try:
        return {"batch_id": batch_id, "results": get_batch_results(batch_id)}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Batch not found")


@router.get("/status/{document_id}")
def get_status(document_id: str):
    try:
        return read_status(document_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Status not found")


@router.get("/document/{document_id}")
def get_document(document_id: str):
    payload_path = DATA_DIR / f"{document_id}.json"
    if not payload_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    return json.loads(payload_path.read_text(encoding="utf-8"))


@router.get("/export/docx/{document_id}")
def export_docx(document_id: str):
    payload_path = DATA_DIR / f"{document_id}.json"
    if not payload_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    document_data = json.loads(payload_path.read_text(encoding="utf-8"))
    output_path = OUTPUT_DIR / f"{document_id}.docx"
    docx_renderer.render(document_data, output_path)

    return FileResponse(path=output_path, filename=output_path.name, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
