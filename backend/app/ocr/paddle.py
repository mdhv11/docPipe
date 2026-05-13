from pathlib import Path
from tempfile import TemporaryDirectory
import os

try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None

from PIL import Image
import pytesseract

try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None


class PaddleOcrExtractor:
    def __init__(self):
        if PaddleOCR is not None:
            self.ocr = PaddleOCR(use_angle_cls=True, lang="en")
        else:
            self.ocr = None

    def ocr_image(self, image_path: Path) -> str:
        if self.ocr:
            result = self.ocr.ocr(str(image_path), cls=True)
            lines = [item[1][0] for page in result for item in page]
            return "\n".join(lines)

        image = Image.open(image_path)
        return pytesseract.image_to_string(image)

    def extract_text(self, image_path: Path) -> str:
        return self.ocr_image(image_path)

    def convert_pdf_to_images(self, pdf_path: Path, temp_dir: str) -> list[Path]:
        if convert_from_path is None:
            raise ImportError(
                "pdf2image is required for PDF OCR. Install it with `pip install pdf2image` and ensure Poppler is available."
            )

        poppler_path = os.getenv("POPPLER_PATH")
        pages = convert_from_path(
            str(pdf_path),
            dpi=300,
            fmt="png",
            output_folder=temp_dir,
            poppler_path=poppler_path,
        )

        page_files = []
        for index, page in enumerate(pages):
            page_file = Path(temp_dir) / f"page_{index}.png"
            page.save(page_file, format="PNG")
            page_files.append(page_file)

        return page_files

    def extract_from_pdf(self, pdf_path: Path) -> str:
        with TemporaryDirectory() as temp_dir:
            page_files = self.convert_pdf_to_images(pdf_path, temp_dir)
            return "\n\n".join(self.ocr_image(page_file) for page_file in page_files)
