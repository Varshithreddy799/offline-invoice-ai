import logging
import os
from fastapi import APIRouter, HTTPException, Query

from database import get_invoice, search_invoices, get_invoice_stats, delete_invoice
from schemas import InvoiceResponse, InvoiceDetailResponse, StatsResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/invoices", response_model=list[InvoiceResponse])
async def list_invoices(
    query: str = Query(default="", description="Search by vendor, invoice number, or date"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    invoices = search_invoices(query=query, limit=limit, offset=offset)
    return [
        InvoiceResponse(
            id=inv["id"],
            filename=inv["filename"],
            vendor=inv["vendor"],
            invoice_number=inv["invoice_number"],
            invoice_date=inv["invoice_date"],
            grand_total=inv["grand_total"],
            status=inv["status"],
            created_at=inv["created_at"],
            processing_time=inv["processing_time"],
            error_message=inv["error_message"],
        )
        for inv in invoices
    ]


@router.get("/invoice/{invoice_id}", response_model=InvoiceDetailResponse)
async def get_invoice_detail(invoice_id: int):
    invoice = get_invoice(invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return InvoiceDetailResponse(
        id=invoice["id"],
        filename=invoice["filename"],
        file_path=invoice["file_path"],
        vendor=invoice["vendor"],
        invoice_number=invoice["invoice_number"],
        invoice_date=invoice["invoice_date"],
        grand_total=invoice["grand_total"],
        original_ocr=invoice["original_ocr"],
        structured_json=invoice["structured_json"],
        status=invoice["status"],
        created_at=invoice["created_at"],
        updated_at=invoice["updated_at"],
        processing_time=invoice["processing_time"],
        cpu_usage=invoice["cpu_usage"],
        memory_usage=invoice["memory_usage"],
        error_message=invoice["error_message"],
    )


@router.delete("/invoice/{invoice_id}")
async def delete_invoice_endpoint(invoice_id: int):
    invoice = get_invoice(invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")

    file_path = invoice.get("file_path")
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError as e:
            logger.warning(f"Failed to delete file {file_path}: {e}")

    deleted = delete_invoice(invoice_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete invoice")
    return {"message": "Invoice deleted successfully", "invoice_id": invoice_id}


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    return get_invoice_stats()
