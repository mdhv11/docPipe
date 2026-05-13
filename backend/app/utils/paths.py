from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = ROOT_DIR / "uploads"
OUTPUT_DIR = ROOT_DIR / "outputs"
DATA_DIR = ROOT_DIR / "data"
TEMP_DIR = ROOT_DIR / "temp"


def ensure_directories() -> None:
    for path in (UPLOAD_DIR, OUTPUT_DIR, DATA_DIR, TEMP_DIR):
        path.mkdir(parents=True, exist_ok=True)
