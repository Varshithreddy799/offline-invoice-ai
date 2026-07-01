import logging
import multiprocessing

from fastapi import APIRouter

from config import DEFAULT_MODEL_PATH, is_deploy, USE_MODEL, USE_OCR
from database import get_invoice_stats
from schemas import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    from routes.upload import llm_service

    stats = get_invoice_stats()
    model_loaded = llm_service is not None and llm_service.is_loaded

    return HealthResponse(
        status="ok",
        model_loaded=model_loaded,
        model_path=str(DEFAULT_MODEL_PATH),
        total_invoices=stats["total"],
        cpu_cores=multiprocessing.cpu_count(),
    )
