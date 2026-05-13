from pathlib import Path


class DocumentRouter:
    @staticmethod
    def classify(file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix in {".jpg", ".jpeg", ".png", ".tiff", ".bmp"}:
            return "image"
        if suffix == ".pdf":
            return "pdf"
        return "image"
