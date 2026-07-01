# Offline Invoice Structurer AI

Convert invoice/receipt images or PDFs into structured JSON — **completely offline** on your local machine. No cloud APIs, no data leaves your computer. Also deployable to **Render** with PostgreSQL.

## Architecture

```
                       ┌─────────────────┐
                       │   Frontend       │
                       │  React + Vite    │
                       └────────┬────────┘
                                │ HTTP / REST
                       ┌────────▼────────┐
                       │   Backend        │
                       │   FastAPI        │
                       └──┬──────────┬───┘
                          │          │
              ┌───────────▼──┐  ┌───▼────────────┐
              │  OCR Service  │  │  LLM Service    │
              │  (Tesseract)  │  │  (llama.cpp)    │
              └───────────────┘  └────────────────┘
                          │          │
                          └────┬─────┘
                               │
                      ┌────────▼────────┐
                      │   Database       │
                      │  SQLite / PG     │
                      └─────────────────┘
```

## Features

- **100% Offline** — No internet required after setup
- **Multi-format Upload** — JPG, PNG, JPEG, PDF (drag & drop)
- **OCR Pipeline** — Grayscale, thresholding, denoise preprocessing
- **AI Extraction** — Local LLM extracts structured invoice data
- **SQLite / PostgreSQL** — SQLite locally, PostgreSQL on Render
- **Search & Filter** — Search by vendor, date, or invoice number
- **Export** — JSON, CSV, and raw OCR text download
- **Dark Mode UI** — Modern responsive interface with Tailwind CSS
- **Multi-page PDF** — Full PDF support with per-page OCR

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend   | Python, FastAPI |
| Frontend  | React, Vite, Tailwind CSS |
| Database  | SQLite (local) / PostgreSQL (Render) |
| OCR       | Tesseract (pytesseract + pdf2image) |
| LLM       | llama.cpp Python bindings (GGUF models) |

## Model Download

The app requires a local GGUF model for AI extraction. Recommended models:

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
winget install UB-Mannheim.TesseractOCR
winget install omar.ahsan.poppler
```

### macOS Setup

```bash
brew install tesseract poppler
```

### Linux Setup

```bash
sudo apt install tesseract-ocr poppler-utils
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|----------|---------|-------------|
| `RENDER` | `false` | Set to `true` on Render deployment |
| `DOCKER` | `false` | Set to `true` in Docker |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server port |
| `DATABASE_URL` | *(empty)* | PostgreSQL connection string (empty = SQLite) |
| `UPLOAD_DIR` | `./uploads` | Upload directory path |
| `MODELS_DIR` | `./models` | GGUF models directory |
| `DATABASE_DIR` | `./database` | SQLite database directory |
| `USE_MODEL` | `true` | Set to `false` to disable LLM loading |
| `LLM_MODEL_NAME` | `phi-3-mini-4k-instruct-q4.gguf` | GGUF filename |
| `LLM_MODEL_PATH` | `./models/...` | Full path to GGUF model |
| `MODEL_CONTEXT` | `2048` | LLM context window size |
| `MODEL_THREADS` | `0` | CPU threads (0 = auto) |
| `USE_OCR` | `true` | Set to `false` to disable OCR |
| `OCR_LANGUAGE` | `eng` | Tesseract language |
| `TESSERACT_PATH` | *(empty)* | Path to Tesseract executable |
| `POPPLER_PATH` | *(empty)* | Path to Poppler bin directory |

## Local Setup

### Backend

```bash
cd offline-invoice-ai
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate
pip install -r backend/requirements.txt

# Place a GGUF model in models/
cd backend
uvicorn main:app --reload
```

API at `http://localhost:8000` | Docs at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

UI at `http://localhost:5173`

## Docker Setup

```bash
# Build and run with PostgreSQL
docker-compose up --build
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

### Docker without GPU

Docker does not have access to your host GPU by default. For CPU-only inference, the app works fine in Docker containers.

## Render Deployment

### One-click deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Manual deployment

1. Push the project to GitHub
2. In Render Dashboard:
   - **New Web Service** (Backend):
     - Build Command: `pip install -r backend/requirements.txt`
     - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
     - Add a PostgreSQL database
     - Set `RENDER=true`, `DATABASE_URL` to the PostgreSQL connection string
     - Set `USE_MODEL=false`, `USE_OCR=false`
   - **New Static Site** (Frontend):
     - Build Command: `cd frontend && npm install && npm run build`
     - Publish Directory: `frontend/dist`
     - Set `VITE_API_URL` to your backend URL

> **Note:** On Render, the GGUF model and Tesseract OCR are disabled by default.
> The API will still accept uploads, store data, and return meaningful errors
> for endpoints that require AI/OCR.

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

## Project Structure

```
offline-invoice-ai/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration & environment
│   ├── database.py          # SQLite / PostgreSQL operations
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
│   │       ├── Dashboard.jsx
│   │       ├── Upload.jsx
│   │       ├── InvoiceViewer.jsx
│   │       ├── Navbar.jsx
│   │       └── ModelCheck.jsx
│   ├── package.json
│   └── vite.config.js
├── models/                  # Place GGUF models here
├── database/                # SQLite database location
├── uploads/                 # Uploaded files
├── scripts/                 # Test and utility scripts
├── .env.example
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── render.yaml
└── README.md
```

## Screenshots

<!-- TODO: Add screenshots -->
<!-- ![Dashboard](screenshots/dashboard.png) -->
<!-- ![Upload](screenshots/upload.png) -->
<!-- ![Invoice Viewer](screenshots/invoice-viewer.png) -->

## Testing

```bash
# Start backend
cd backend && uvicorn main:app --reload &

# Generate a sample invoice
python scripts/generate_sample_invoice.py

# Run API tests
python scripts/test_api.py ../uploads/sample_invoice.png
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
- **Render deployment** → Meaningful JSON errors instead of crashes

## License

MIT
