import os
import sys
import multiprocessing
from pathlib import Path
from functools import lru_cache


BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent


@lru_cache()
def is_render() -> bool:
    return os.getenv("RENDER", "").lower() in ("true", "1", "yes")


@lru_cache()
def is_docker() -> bool:
    return os.getenv("DOCKER", "").lower() in ("true", "1", "yes")


def is_deploy() -> bool:
    return is_render() or is_docker()


UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(ROOT_DIR / "uploads")))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", "")

DATABASE_DIR = Path(os.getenv("DATABASE_DIR", str(ROOT_DIR / "database")))
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "invoices.db"

TESSERACT_PATH = os.getenv("TESSERACT_PATH", "")
POPPLER_PATH = os.getenv("POPPLER_PATH", "")

if TESSERACT_PATH:
    os.environ["TESSERACT_PATH"] = TESSERACT_PATH

MODELS_DIR = Path(os.getenv("MODELS_DIR", str(ROOT_DIR / "models")))
MODELS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "phi-3-mini-4k-instruct-q4.gguf")
DEFAULT_MODEL_PATH = os.getenv("LLM_MODEL_PATH", str(MODELS_DIR / DEFAULT_MODEL_NAME))

MODEL_CONTEXT = int(os.getenv("MODEL_CONTEXT", "2048"))
MODEL_THREADS = int(os.getenv("MODEL_THREADS", "0"))
if MODEL_THREADS == 0:
    MODEL_THREADS = multiprocessing.cpu_count()

USE_MODEL = os.getenv("USE_MODEL", "").lower() not in ("false", "0", "no")
USE_OCR = os.getenv("USE_OCR", "").lower() not in ("false", "0", "no")

OCR_LANGUAGE = os.getenv("OCR_LANGUAGE", "eng")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
