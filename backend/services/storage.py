import csv
import json
import logging
import io
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def export_invoice_json(invoice: dict) -> str:
    try:
        data = json.loads(invoice.get("structured_json", "{}"))
    except json.JSONDecodeError:
        data = {"error": "Invalid stored JSON", "raw": invoice.get("structured_json", "")}
    data["_meta"] = {
        "id": invoice["id"],
        "filename": invoice["filename"],
        "created_at": invoice["created_at"],
        "status": invoice["status"],
    }
    return json.dumps(data, indent=2)


def export_invoice_csv(invoice: dict) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Field", "Value"])
    try:
        data = json.loads(invoice.get("structured_json", "{}"))
    except json.JSONDecodeError:
        data = {}

    writer.writerow(["Filename", invoice.get("filename", "")])
    writer.writerow(["Vendor", data.get("vendor", "")])
    writer.writerow(["Invoice Number", data.get("invoice_number", "")])
    writer.writerow(["Invoice Date", data.get("invoice_date", "")])
    writer.writerow(["Subtotal", data.get("subtotal", "")])
    writer.writerow(["Tax", data.get("tax", "")])
    writer.writerow(["Grand Total", data.get("grand_total", "")])
    writer.writerow(["Payment Method", data.get("payment_method", "")])
    writer.writerow([])
    writer.writerow(["Item Name", "Quantity", "Unit Price", "Total"])
    for item in data.get("items", []):
        writer.writerow([
            item.get("name", ""),
            item.get("quantity", ""),
            item.get("unit_price", ""),
            item.get("total", ""),
        ])
    writer.writerow([])
    writer.writerow(["Status", invoice.get("status", "")])
    writer.writerow(["Processing Time (s)", invoice.get("processing_time", 0)])
    return output.getvalue()


def get_ocr_text(invoice: dict) -> str:
    return invoice.get("original_ocr", "No OCR text available.")
