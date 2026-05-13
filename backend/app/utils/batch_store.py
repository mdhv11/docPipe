import json
from pathlib import Path
from typing import List

from app.utils.paths import DATA_DIR


def get_batch_path(batch_id: str) -> Path:
    return DATA_DIR / f"batch_{batch_id}.json"


def create_batch(document_ids: List[str]) -> str:
    import uuid
    batch_id = uuid.uuid4().hex

    batch_data = {
        "batch_id": batch_id,
        "document_ids": document_ids,
        "status": "processing",
        "created_at": None,  # Will be set when batch starts
        "completed_at": None,
        "errors": [],
        "retry_count": 0,
    }

    path = get_batch_path(batch_id)
    path.write_text(json.dumps(batch_data, indent=2, ensure_ascii=False), encoding="utf-8")
    return batch_id


def update_batch_status(batch_id: str, status: str, errors: List[str] = None) -> None:
    path = get_batch_path(batch_id)
    if not path.exists():
        return

    batch_data = json.loads(path.read_text(encoding="utf-8"))
    batch_data["status"] = status
    if errors:
        batch_data["errors"].extend(errors)

    if status == "completed":
        import datetime
        batch_data["completed_at"] = datetime.datetime.now().isoformat()

    path.write_text(json.dumps(batch_data, indent=2, ensure_ascii=False), encoding="utf-8")


def get_batch_status(batch_id: str) -> dict:
    path = get_batch_path(batch_id)
    if not path.exists():
        raise FileNotFoundError(f"Batch not found: {batch_id}")

    return json.loads(path.read_text(encoding="utf-8"))


def get_batch_results(batch_id: str) -> List[dict]:
    batch_data = get_batch_status(batch_id)
    results = []

    for doc_id in batch_data["document_ids"]:
        try:
            from app.utils.status_store import read_status
            status = read_status(doc_id)
            results.append({
                "document_id": doc_id,
                "status": status.get("status", "unknown"),
                "current_task": status.get("current_task", ""),
                "error": status.get("error"),
            })
        except FileNotFoundError:
            results.append({
                "document_id": doc_id,
                "status": "not_found",
                "current_task": "",
                "error": "Document status not found",
            })

    return results