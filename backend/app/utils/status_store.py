import json
from pathlib import Path

from app.utils.paths import DATA_DIR


def get_status_path(document_id: str) -> Path:
    return DATA_DIR / f"{document_id}.status.json"


def write_status(
    document_id: str,
    status: str,
    current_task: str = "",
    total_pages: int | None = None,
    processed_pages: int | None = None,
    error: str | None = None,
) -> dict:
    payload = {
        "document_id": document_id,
        "status": status,
        "current_task": current_task,
        "total_pages": total_pages,
        "processed_pages": processed_pages,
        "error": error,
    }
    path = get_status_path(document_id)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def read_status(document_id: str) -> dict:
    path = get_status_path(document_id)
    if not path.exists():
        raise FileNotFoundError(f"Status file not found for {document_id}")
    return json.loads(path.read_text(encoding="utf-8"))
