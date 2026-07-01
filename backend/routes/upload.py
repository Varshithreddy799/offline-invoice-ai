import json
import logging
import time
import os
import psutil
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse

from config import UPLOAD_DIR, USE_MODEL, USE_OCR
from database import create_invoice, update_invoice, get_invoice
from services.ocr import extract_text, SUPPORTED_EXTENSIONS, OCR_AVAILABLE
from services.llm import LLMService
from services.storage import export_invoice_json, export_invoice_csv, get_ocr_text
from schemas import UploadResponse

logger = logging.getLogger(__name__)

router = APIRouter()
llm_service: LLMService = None


def set_llm_service(service: LLMService) -> None:
    global llm_service
    llm_service = service


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Supported: {', '.join(SUPPORTED_EXTENSIONS)}",
        )

    try:
        file_path = UPLOAD_DIR / f"{int(time.time())}_{file.filename}"
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        invoice_id = create_invoice(file.filename, str(file_path))
        logger.info(f"Uploaded {file.filename} -> invoice #{invoice_id}")
        return UploadResponse(invoice_id=invoice_id, filename=file.filename, message="File uploaded successfully")
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/process/{invoice_id}")
async def process_invoice(invoice_id: int):
    invoice = get_invoice(invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if not USE_MODEL or not llm_service or not llm_service.is_loaded:
        error_msg = (
            "Model not available. Place a GGUF model in models/ "
            "or set USE_MODEL=false if running without AI."
        )
        update_invoice(invoice_id, status="error", error_message=error_msg)
        raise HTTPException(status_code=503, detail=error_msg)

    if not USE_OCR or not OCR_AVAILABLE:
        error_msg = "OCR not available. Install Tesseract and Poppler, or set USE_OCR=false."
        update_invoice(invoice_id, status="error", error_message=error_msg)
        raise HTTPException(status_code=503, detail=error_msg)

    start_time = time.time()
    cpu_start = psutil.cpu_percent(interval=None)
    process = psutil.Process()
    mem_start = process.memory_info().rss / (1024 * 1024)

    try:
        update_invoice(invoice_id, status="processing")

        file_path = invoice["file_path"]
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ocr_text = extract_text(file_path)
        if not ocr_text.strip():
            raise ValueError("OCR produced no text. The image may be unreadable.")

        result = llm_service.extract(ocr_text)
        if "error" in result:
            update_invoice(
                invoice_id,
                status="error",
                error_message=result["error"],
                original_ocr=ocr_text,
            )
            raise HTTPException(status_code=422, detail=result["error"])

        elapsed = time.time() - start_time
        mem_end = process.memory_info().rss / (1024 * 1024)

        update_invoice(
            invoice_id,
            original_ocr=ocr_text,
            structured_json=json.dumps(result),
            vendor=result.get("vendor", ""),
            invoice_number=result.get("invoice_number", ""),
            invoice_date=result.get("invoice_date", ""),
            grand_total=result.get("grand_total", ""),
            processing_time=round(elapsed, 2),
            cpu_usage=psutil.cpu_percent(interval=None),
            memory_usage=round(mem_end - mem_start, 2),
            status="completed",
        )

        invoice = get_invoice(invoice_id)
        return {
            "invoice_id": invoice_id,
            "status": "completed",
            "processing_time": round(elapsed, 2),
            "result": json.loads(invoice["structured_json"]),
        }

    except FileNotFoundError as e:
        update_invoice(invoice_id, status="error", error_message=str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        update_invoice(invoice_id, status="error", error_message=str(e))
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Processing failed for invoice #{invoice_id}: {e}")
        update_invoice(invoice_id, status="error", error_message=str(e))
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.post("/process/{invoice_id}/stream")
async def process_invoice_stream(invoice_id: int):
    invoice = get_invoice(invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if not USE_MODEL or not llm_service or not llm_service.is_loaded:
        raise HTTPException(status_code=503, detail="Model not available")

    if not USE_OCR or not OCR_AVAILABLE:
        raise HTTPException(status_code=503, detail="OCR not available")

    async def event_generator():
        yield f"data: {json.dumps({'type': 'status', 'message': 'Starting OCR...'})}\n\n"
        try:
            file_path = invoice["file_path"]
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            ocr_text = extract_text(file_path)
            if not ocr_text.strip():
                raise ValueError("OCR produced no text.")

            yield f"data: {json.dumps({'type': 'status', 'message': 'OCR complete. Running AI extraction...'})}\n\n"

            full_text = ""
            for token in llm_service.extract_stream(ocr_text):
                full_text += token
                yield f"data: {json.dumps({'type': 'token', 'token': token})}\n\n"

            cleaned = llm_service._clean_json(full_text) if hasattr(llm_service, '_clean_json') else full_text
            result = json.loads(cleaned)
            update_invoice(
                invoice_id,
                original_ocr=ocr_text,
                structured_json=json.dumps(result),
                vendor=result.get("vendor", ""),
                invoice_number=result.get("invoice_number", ""),
                invoice_date=result.get("invoice_date", ""),
                grand_total=result.get("grand_total", ""),
                status="completed",
            )
            yield f"data: {json.dumps({'type': 'complete', 'result': result})}\n\n"
        except Exception as e:
            logger.error(f"Stream processing failed: {e}")
            update_invoice(invoice_id, status="error", error_message=str(e))
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/invoice/{invoice_id}/export/json")
async def export_json(invoice_id: int):
    invoice = get_invoice(invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return StreamingResponse(
        iter([export_invoice_json(invoice)]),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="invoice_{invoice_id}.json"'},
    )


@router.get("/invoice/{invoice_id}/export/csv")
async def export_csv(invoice_id: int):
    invoice = get_invoice(invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return StreamingResponse(
        iter([export_invoice_csv(invoice)]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="invoice_{invoice_id}.csv"'},
    )


@router.get("/invoice/{invoice_id}/export/ocr")
async def export_ocr(invoice_id: int):
    invoice = get_invoice(invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return StreamingResponse(
        iter([get_ocr_text(invoice)]),
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="invoice_{invoice_id}_ocr.txt"'},
    )
