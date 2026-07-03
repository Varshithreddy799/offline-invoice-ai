# 🧾 Offline Invoice AI

An AI-powered invoice extraction system that works completely **offline** using OCR and a local Large Language Model (LLM). The application extracts structured information from invoice PDFs and images into JSON format without sending any data to the cloud.

---

## 🚀 Features

- 📄 Upload invoice images or PDF files
- 🔍 OCR using Tesseract
- 🤖 Local AI processing using Phi-3 Mini GGUF
- 📦 Extracts:
  - Vendor Name
  - Invoice Number
  - Invoice Date
  - Items
  - Quantity
  - Unit Price
  - Total
  - Tax
  - Grand Total
  - Payment Method
- 💾 Stores processed invoices locally
- 📊 Dashboard to view uploaded invoices
- 🌐 React + FastAPI architecture
- 🔒 Privacy-friendly (No internet required for local processing)

---

# 🏗️ Tech Stack

### Frontend
- React.js
- Vite
- Tailwind CSS

### Backend
- FastAPI
- Python
- SQLite

### AI & OCR
- Phi-3 Mini GGUF (Local LLM)
- llama-cpp-python
- Tesseract OCR
- Poppler
- pdf2image
- Pillow

---

# 📂 Project Structure

```
offline-invoice-ai
│
├── backend/
│   ├── routes/
│   ├── services/
│   ├── config.py
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── models/
│
├── uploads/
│
├── database/
│
├── render.yaml
│
└── README.md
```

---

# ⚙️ Local Installation

## 1. Clone Repository

```bash
git clone https://github.com/Varshithreddy799/offline-invoice-ai.git
cd offline-invoice-ai
```

---

## 2. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at

```
http://localhost:8000
```

---

## 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at

```
http://localhost:5173
```

---

# 📦 Requirements

Install:

- Python 3.11+
- Node.js
- Tesseract OCR
- Poppler
- GGUF Model (Phi-3 Mini Instruct)

Place the model inside

```
models/
```

Example

```
models/
└── phi-3-mini-4k-instruct-q4.gguf
```

---

# 🌍 Live Demo

Frontend

https://offline-invoice-ai-frontend.onrender.com/

Backend

https://offline-invoice-ai-backend.onrender.com/

API Documentation

https://offline-invoice-ai-backend.onrender.com/docs

---

# ⚠️ Cloud Deployment Notice

The cloud deployment runs in **demonstration mode** because the local GGUF model and OCR dependencies are too large for the free Render environment.

Therefore:

- ✅ Frontend is fully deployed.
- ✅ Backend API is deployed.
- ✅ Dashboard and UI are functional.
- ❌ Local AI model is disabled in the cloud.
- ❌ OCR processing is disabled in the cloud.

**The complete AI functionality, including OCR and offline invoice extraction, works when running the project locally with the required dependencies installed.**

---

# 🔒 Privacy

All invoice processing is performed locally when running the application on your machine.

No invoice data is uploaded to external AI services.

---

# 📸 Screenshots

_Add screenshots of your application here._

Example:

- Dashboard
- Upload Screen
- Processed Invoice
- API Docs

---

# 📈 Future Enhancements

- Multi-language OCR
- Batch invoice processing
- Export to Excel/CSV
- PostgreSQL support
- Docker deployment
- Authentication
- Analytics Dashboard

---

# 👨‍💻 Author

**Varshith Reddy**

GitHub

https://github.com/Varshithreddy799

Project Repository

https://github.com/Varshithreddy799/offline-invoice-ai

GitLab

https://code.swecha.org/sangem_varshith/offline-invoice-ai

---

# 📜 License

This project is developed for educational and hackathon purposes.