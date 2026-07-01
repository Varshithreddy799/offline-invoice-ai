from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class InvoiceItem(BaseModel):
    name: str = ""
    quantity: str = ""
    unit_price: str = ""
    total: str = ""


class StructuredInvoice(BaseModel):
    vendor: str = ""
    invoice_number: str = ""
    invoice_date: str = ""
    items: list[InvoiceItem] = []
    subtotal: str = ""
    tax: str = ""
    grand_total: str = ""
    payment_method: str = ""


class InvoiceResponse(BaseModel):
    id: int
    filename: str
    vendor: str
    invoice_number: str
    invoice_date: str
    grand_total: str
    status: str
    created_at: str
    processing_time: float
    error_message: str

    class Config:
        from_attributes = True


class InvoiceDetailResponse(InvoiceResponse):
    file_path: str
    original_ocr: str
    structured_json: str
    cpu_usage: float
    memory_usage: float
    updated_at: str


class StatsResponse(BaseModel):
    total: int
    processed: int
    failed: int
    pending: int


class HealthResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    status: str
    model_loaded: bool
    model_path: str
    total_invoices: int
    cpu_cores: int
    version: str = "1.0.0"


class UploadResponse(BaseModel):
    invoice_id: int
    filename: str
    message: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
