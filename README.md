# Offline Invoice Structurer AI

Convert invoice/receipt images or PDFs into structured JSON — **completely offline** on your local machine. No cloud APIs, no data leaves your computer.

## Architecture

```
Image/PDF  →  OCR (Tesseract)  →  Clean Text  →  Local LLM (GGUF)  →  Structured JSON  →  SQLite  →  Dashboard
```

## Features

- **100% Offline** — No internet required after setup
- **Multi-format Upload** — JPG, PNG, JPEG, PDF (drag & drop)
- **OCR Pipeline** — Grayscale, thresholding, denoise preprocessing
- **AI Extraction** — Local LLM extracts structured invoice data
- **SQLite Storage** — All data stored locally in SQLite
- **Search & Filter** — Search by vendor, date, or invoice number
- **Export** — JSON, CSV, and raw OCR text download
- **Dark Mode UI** — Modern responsive interface with Tailwind CSS
- **Multi-page PDF** — Full PDF support with per-page OCR

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend   | Python, FastAPI |
| Frontend  | React, Vite, Tailwind CSS |
| Database  | SQLite |
| OCR       | Tesseract (pytesseract + pdf2image) |
| LLM       | llama.cpp Python bindings (GGUF models) |

## Model Download

The app requires a local GGUF model. Recommended models (choose one):

| Model | Size | Link |
|-------|------|------|
| Phi-3 Mini 4K Instruct Q4 | ~2.2 GB | [Hugging Face](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf) |
| SmolLM2 1.7B Q4 | ~1 GB | [Hugging Face](https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct-GGUF) |
| TinyLlama 1.1B Q4 | ~700 MB | [Hugging Face](https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF) |
| Gemma 3 1B Q4 | ~700 MB | [Hugging Face](https://huggingface.co/bartowski/gemma-3-1b-it-GGUF) |

**Download steps:**
1. Download a `.gguf` file from one of the links above
2. Place it in the `models/` directory
3. Update `.env` if using a different filename

## Prerequisites

- Python 3.10+
- Node.js 18+
- Tesseract OCR ([Install Guide](https://github.com/tesseract-ocr/tesseract))
- Poppler (for PDF processing)

### Windows Setup

```powershell
# Install Tesseract
winget install UB-Mannheim.TesseractOCR
# or download from: https://github.com/UB-Mannheim/tesseract/wiki

# Install Poppler
winget install omar.ahsan.poppler
# or download from: https://github.com/oschwartz10612/poppler-windows/releases/
```

### macOS Setup

```bash
brew install tesseract poppler
```

### Linux Setup

```bash
sudo apt install tesseract-ocr poppler-utils
```

## Installation

### Backend

```bash
# Navigate to project root
cd offline-invoice-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r backend/requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Running Locally

### 1. Place a GGUF model in `models/`

```bash
# Example: Phi-3 Mini
# Download phi-3-mini-4k-instruct-q4.gguf and place in models/
```

### 2. Start the backend

```bash
cd backend
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### 3. Start the frontend

```bash
cd frontend
npm run dev
```

The UI will be available at `http://localhost:5173`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/upload` | Upload invoice file |
| POST   | `/process/{id}` | Process invoice (OCR + LLM) |
| POST   | `/process/{id}/stream` | Process with streaming tokens |
| GET    | `/invoices` | List all invoices (with search) |
| GET    | `/invoice/{id}` | Get invoice details |
| DELETE | `/invoice/{id}` | Delete an invoice |
| GET    | `/stats` | Get dashboard statistics |
| GET    | `/health` | Health check with model status |
| GET    | `/invoice/{id}/export/json` | Export as JSON |
| GET    | `/invoice/{id}/export/csv` | Export as CSV |
| GET    | `/invoice/{id}/export/ocr` | Download OCR text |

## CPU Optimization

- **4-bit GGUF quantization** — Reduces memory and accelerates inference
- **Auto thread detection** — Automatically uses all available CPU cores
- **Context size: 2048** — Optimal balance for invoice processing
- **No GPU required** — Runs entirely on CPU

Configure via `.env`:
```
MODEL_THREADS=0    # 0 = auto-detect CPU cores
MODEL_CONTEXT=2048 # Context window size
```

## Project Structure

```
offline-invoice-ai/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration & environment
│   ├── database.py          # SQLite operations
│   ├── schemas.py           # Pydantic models
│   ├── services/
│   │   ├── ocr.py           # OCR preprocessing & extraction
│   │   ├── llm.py           # LLM inference with llama.cpp
│   │   └── storage.py       # Export utilities
│   ├── routes/
│   │   ├── upload.py        # Upload & process endpoints
│   │   ├── invoices.py      # CRUD for invoices
│   │   └── health.py        # Health check
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Root component with routing
│   │   ├── api.js           # API client
│   │   └── components/
│   │       ├── Dashboard.jsx      # Stats, search, invoice list
│   │       ├── Upload.jsx         # Drag & drop upload
│   │       ├── InvoiceViewer.jsx  # JSON/OCR viewer with export
│   │       ├── Navbar.jsx         # Top navigation
│   │       └── ModelCheck.jsx     # Model status warnings
│   ├── package.json
│   └── vite.config.js
├── models/                  # Place GGUF models here
├── database/                # SQLite database location
├── uploads/                 # Uploaded files
├── .env.example
├── docker-compose.yml
└── README.md
```

## Error Handling

The app gracefully handles:
- **Unreadable images** → OCR returns empty text, clear error shown
- **OCR failure** → Proper exception handling with user feedback
- **Model timeout** → Retry logic with fallback JSON parsing
- **Invalid JSON** → Auto-retry LLM extraction (3 attempts)
- **Missing PDF** → File existence check before processing
- **Corrupt images** → PIL/Pillow error handling
- **No model present** → "Local model missing" message with instructions
- **Empty files** → Size validation on upload

## Docker Support

```bash
# Build and run with Docker Compose
docker-compose up --build
```

**Note:** Docker does not have access to your host GPU by default. For CPU-only inference, the app works fine in Docker containers.

## Testing

```bash
# Start backend
cd backend && uvicorn main:app --reload &

# Test health endpoint
curl http://localhost:8000/health

# Upload a test invoice
curl -X POST -F "file=@sample_invoice.jpg" http://localhost:8000/upload

# Process it (replace {id} with actual invoice ID)
curl -X POST http://localhost:8000/process/{id}
```

## License

MIT

## Hackathon Project

This project was built for an offline-first AI hackathon. The core idea: **AI should work without the cloud.** By combining local OCR with a quantized LLM running via llama.cpp, we get structured data extraction from documents without sending sensitive financial data to any external service.
