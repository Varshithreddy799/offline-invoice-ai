import os
import multiprocessing
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

DATABASE_DIR = ROOT_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)
DATABASE_PATH = DATABASE_DIR / "invoices.db"

MODELS_DIR = ROOT_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

DEFAULT_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "phi-3-mini-4k-instruct-q4.gguf")
DEFAULT_MODEL_PATH = os.getenv("LLM_MODEL_PATH", str(MODELS_DIR / DEFAULT_MODEL_NAME))
MODEL_CONTEXT = int(os.getenv("MODEL_CONTEXT", "2048"))
MODEL_THREADS = int(os.getenv("MODEL_THREADS", "0"))
if MODEL_THREADS == 0:
    MODEL_THREADS = multiprocessing.cpu_count()

OCR_LANGUAGE = os.getenv("OCR_LANGUAGE", "eng")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
