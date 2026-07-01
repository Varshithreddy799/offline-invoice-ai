import logging
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageFilter

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}


def preprocess_image(image: Image.Image) -> Image.Image:
    image = image.convert("L")
    image = image.filter(ImageFilter.SHARPEN)
    image = image.point(lambda x: 0 if x < 128 else 255, "1")
    return image


def extract_text_from_image(image_path: str) -> str:
    try:
        image = Image.open(image_path)
        processed = preprocess_image(image)
        text = pytesseract.image_to_string(processed)
        return text.strip()
    except Exception as e:
        logger.error(f"OCR failed for image {image_path}: {e}")
        raise


def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        POPPLER_PATH = r"C:\Users\varsh\Downloads\Release-26.02.0-0\poppler-26.02.0\Library\bin"

        images = convert_from_path(
            pdf_path,
            dpi=300,
            poppler_path=POPPLER_PATH
        )

        text_parts = []

        for i, image in enumerate(images):
            processed = preprocess_image(image)
            page_text = pytesseract.image_to_string(processed)
            text_parts.append(f"--- Page {i + 1} ---\n{page_text.strip()}")

        return "\n\n".join(text_parts)

    except Exception as e:
        logger.error(f"OCR failed for PDF {pdf_path}: {e}")
        raise


def extract_text(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {ext}")
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    return extract_text_from_image(file_path)
