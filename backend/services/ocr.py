from __future__ import annotations

import logging
from pathlib import Path

from config import TESSERACT_PATH, POPPLER_PATH, USE_OCR
from PIL import Image, ImageFilter

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}

if USE_OCR:
    try:
        import pytesseract

        if TESSERACT_PATH:
            pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

        from pdf2image import convert_from_path

        OCR_AVAILABLE = True

    except ImportError:
        OCR_AVAILABLE = False
        logger.warning("OCR dependencies not installed. OCR will be unavailable.")
else:
    OCR_AVAILABLE = False
    logger.info("OCR disabled via USE_OCR=false")


def preprocess_image(image: Image.Image) -> Image.Image:
    image = image.convert("L")
    image = image.filter(ImageFilter.SHARPEN)
    image = image.point(lambda x: 0 if x < 128 else 255, "1")
    return image


def extract_text_from_image(image_path: str) -> str:
    if not OCR_AVAILABLE:
        raise RuntimeError(
            "OCR is not available. Install pytesseract and pdf2image, or set USE_OCR=true."
        )

    try:
        image = Image.open(image_path)
        processed = preprocess_image(image)
        text = pytesseract.image_to_string(processed)
        return text.strip()

    except Exception as e:
        logger.error(f"OCR failed for image {image_path}: {e}")
        raise


def extract_text_from_pdf(pdf_path: str) -> str:
    if not OCR_AVAILABLE:
        raise RuntimeError(
            "OCR is not available. Install pytesseract and pdf2image, or set USE_OCR=true."
        )

    try:
        kwargs = {"dpi": 300}

        if POPPLER_PATH:
            kwargs["poppler_path"] = POPPLER_PATH

        images = convert_from_path(pdf_path, **kwargs)

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
    if not OCR_AVAILABLE:
        raise RuntimeError(
            "OCR is unavailable on this server. "
            "This feature requires Tesseract and Poppler to be installed."
        )

    ext = Path(file_path).suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {ext}")

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)

    return extract_text_from_image(file_path)