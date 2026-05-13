# docPipe

An AI document reconstruction pipeline prototype for scanned images, PDFs, and screenshots.

## What this scaffold includes

- FastAPI backend at `backend/app`
- OCR helper with PaddleOCR fallback to `pytesseract`
- Image preprocessing with OpenCV
- llama.cpp integration for semantic JSON reconstruction
- DOCX export using `python-docx`

## Getting started

1. Install Python dependencies:

```bash
cd /home/mdhv11/Codes/docPipe/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Install `llama.cpp` separately:

```bash
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
make
```

3. Install Poppler for PDF rendering and download a supported GGUF model.

On Ubuntu/Debian:

```bash
sudo apt-get install poppler-utils
```

Then set environment variables:

```bash
export LLAMA_CPP_BIN=/path/to/llama.cpp/main/llama
export LLAMA_CPP_MODEL=/path/to/model.gguf
export POPPLER_PATH=/usr/bin
```

4. Run the server:

```bash
cd /home/mdhv11/Codes/docPipe/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API endpoints

- `POST /upload` — upload a single image or PDF
- `POST /upload/batch` — upload multiple files for batch processing
- `GET /batch/{batch_id}` — get batch processing status and results summary
- `GET /batch/{batch_id}/results` — get detailed results for all documents in batch
- `GET /status/{id}` — get current processing progress and page status (JSON)
- `GET /document/{id}` — retrieve reconstructed JSON after processing completes
- `GET /export/docx/{id}` — download a DOCX file

### Batch Processing

Upload multiple documents at once and track their processing as a group:

```bash
# Upload multiple files
curl -X POST "http://localhost:8000/upload/batch" \
  -F "files=@document1.pdf" \
  -F "files=@document2.jpg" \
  -F "files=@document3.png"

# Response includes batch_id and individual document_ids
{
  "batch_id": "abc123...",
  "document_ids": ["doc1", "doc2", "doc3"],
  "total_files": 3,
  "status": "processing"
}

# Check batch progress
curl "http://localhost:8000/batch/abc123"

# Get detailed results
curl "http://localhost:8000/batch/abc123/results"
```

### Error Recovery & Retry Logic

The system includes automatic retry logic for resilient processing:

- **OCR Operations**: Retries up to 2 times with exponential backoff (1s, 2s delays)
- **LLM Inference**: Retries up to 2 times with exponential backoff (2s, 4s delays)
- **Batch Processing**: Continues processing other files even if some fail
- **Timeout Handling**: 1-hour timeout for batch operations with monitoring

Failed operations are logged and can be retried by re-uploading the specific document.

### Quick start

Run both services with the development script:

```bash
./run-dev.sh
```

This will:
- Set up the Python virtual environment (if needed)
- Install dependencies
- Start the backend on port 8000
- Start the frontend on port 3000

### Manual setup

```bash
cd frontend
npm install
npm run dev
```

### Running both frontend and backend

You can run both services simultaneously:

```bash
# Terminal 1 - Backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Or use a process manager like `concurrently`:

```bash
npm install -g concurrently
concurrently "cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" "cd frontend && npm run dev"
```

- Drag-and-drop file upload
- Real-time status polling (every 2 seconds)
- Progress bar for multi-page documents
- Download reconstructed DOCX files
- Error handling and status display

- The current version uses llama.cpp for semantic structuring only.
- PDF OCR is left as a future extension.
- For best results, use a local model compatible with llama.cpp.
