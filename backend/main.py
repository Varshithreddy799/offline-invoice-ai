import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import HOST, PORT, DEFAULT_MODEL_PATH
from database import init_db
from services.llm import LLMService
from routes.upload import router as upload_router, set_llm_service
from routes.invoices import router as invoices_router
from routes.health import router as health_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Database initialized")

    llm = LLMService(model_path=str(DEFAULT_MODEL_PATH))
    set_llm_service(llm)
    if llm.is_loaded:
        logger.info(f"LLM model loaded: {DEFAULT_MODEL_PATH}")
    else:
        logger.warning(f"LLM model not found at {DEFAULT_MODEL_PATH}. Place a GGUF model in the models/ directory.")
    yield


app = FastAPI(
    title="Offline Invoice Structurer AI",
    description="Convert invoice/receipt images to structured JSON locally.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(invoices_router)
app.include_router(health_router)


@app.get("/")
async def root():
    return {
        "app": "Offline Invoice Structurer AI",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
