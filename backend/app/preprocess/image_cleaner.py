import cv2
from pathlib import Path


class ImageCleaner:
    def clean(self, image_path: Path) -> Path:
        image = cv2.imread(str(image_path))
        if image is None:
            return image_path

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        cleaned_path = image_path.parent / f"cleaned_{image_path.name}"
        cv2.imwrite(str(cleaned_path), thresh)
        return cleaned_path
