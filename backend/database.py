import sqlite3
import json
import logging
from datetime import datetime
from typing import Optional
from contextlib import contextmanager

from config import DATABASE_PATH

logger = logging.getLogger(__name__)

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL DEFAULT '',
                original_ocr TEXT DEFAULT '',
                structured_json TEXT DEFAULT '{}',
                vendor TEXT DEFAULT '',
                invoice_number TEXT DEFAULT '',
                invoice_date TEXT DEFAULT '',
                grand_total TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processing_time REAL DEFAULT 0,
                cpu_usage REAL DEFAULT 0,
                memory_usage REAL DEFAULT 0,
                status TEXT DEFAULT 'pending',
                error_message TEXT DEFAULT ''
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_invoices_vendor
            ON invoices(vendor)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_invoices_date
            ON invoices(invoice_date)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_invoices_number
            ON invoices(invoice_number)
        """)
        conn.commit()

def create_invoice(filename: str, file_path: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO invoices (filename, file_path, status) VALUES (?, ?, 'uploaded')",
            (filename, file_path)
        )
        conn.commit()
        return cursor.lastrowid

def update_invoice(
    invoice_id: int,
    original_ocr: Optional[str] = None,
    structured_json: Optional[str] = None,
    vendor: Optional[str] = None,
    invoice_number: Optional[str] = None,
    invoice_date: Optional[str] = None,
    grand_total: Optional[str] = None,
    processing_time: Optional[float] = None,
    cpu_usage: Optional[float] = None,
    memory_usage: Optional[float] = None,
    status: Optional[str] = None,
    error_message: Optional[str] = None,
) -> None:
    fields = {}
    if original_ocr is not None:
        fields["original_ocr"] = original_ocr
    if structured_json is not None:
        fields["structured_json"] = structured_json
    if vendor is not None:
        fields["vendor"] = vendor
    if invoice_number is not None:
        fields["invoice_number"] = invoice_number
    if invoice_date is not None:
        fields["invoice_date"] = invoice_date
    if grand_total is not None:
        fields["grand_total"] = grand_total
    if processing_time is not None:
        fields["processing_time"] = processing_time
    if cpu_usage is not None:
        fields["cpu_usage"] = cpu_usage
    if memory_usage is not None:
        fields["memory_usage"] = memory_usage
    if status is not None:
        fields["status"] = status
    if error_message is not None:
        fields["error_message"] = error_message

    if not fields:
        return

    fields["updated_at"] = datetime.utcnow().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [invoice_id]

    with get_connection() as conn:
        conn.execute(
            f"UPDATE invoices SET {set_clause} WHERE id = ?",
            values
        )
        conn.commit()

def get_invoice(invoice_id: int) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM invoices WHERE id = ?", (invoice_id,)
        ).fetchone()
        if row is None:
            return None
        return dict(row)

def search_invoices(
    query: str = "",
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    with get_connection() as conn:
        if query:
            pattern = f"%{query}%"
            rows = conn.execute(
                """SELECT * FROM invoices
                   WHERE vendor LIKE ?
                      OR invoice_number LIKE ?
                      OR invoice_date LIKE ?
                      OR filename LIKE ?
                   ORDER BY created_at DESC
                   LIMIT ? OFFSET ?""",
                (pattern, pattern, pattern, pattern, limit, offset)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM invoices ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset)
            ).fetchall()
        return [dict(r) for r in rows]

def get_invoice_stats() -> dict:
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM invoices").fetchone()[0]
        processed = conn.execute(
            "SELECT COUNT(*) FROM invoices WHERE status = 'completed'"
        ).fetchone()[0]
        failed = conn.execute(
            "SELECT COUNT(*) FROM invoices WHERE status = 'error'"
        ).fetchone()[0]
        pending = conn.execute(
            "SELECT COUNT(*) FROM invoices WHERE status NOT IN ('completed', 'error')"
        ).fetchone()[0]
        return {
            "total": total,
            "processed": processed,
            "failed": failed,
            "pending": pending,
        }

def delete_invoice(invoice_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM invoices WHERE id = ?", (invoice_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
