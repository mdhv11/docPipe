# AI Document Reconstruction Pipeline

## Goal

Build an AI-powered pipeline that converts:
- scanned images
- handwritten notes
- screenshots
- PDFs

into:
- structured JSON
- editable DOCX
- clean PDFs

while preserving:
- headings
- paragraphs
- tables
- lists
- document hierarchy
- reading order

---

# Core Philosophy

Instead of:

Image → OCR → Plain Text

We want:

Image → Semantic Understanding → Structured Document

The system should reconstruct the document intelligently.

---

# Final Architecture

```text
Frontend (React)
    ↓
FastAPI Backend
    ↓
Preprocessing (OpenCV)
    ↓
Document Routing
    ├── Nougat
    ├── PaddleOCR
    └── Qwen2.5-VL
    ↓
Structured JSON
    ↓
DOCX/PDF Renderer
    ↓
Downloadable Output
```

---

# Why Multiple Models?

Different models are good at different things.

| Component | Responsibility |
|---|---|
| OpenCV | Image cleanup |
| PaddleOCR | Accurate text extraction |
| Nougat | Scientific/research paper parsing |
| Qwen2.5-VL | Semantic layout understanding |
| Renderer | DOCX/PDF generation |

---

# Role of Nougat

## What Nougat Does Best

Nougat is extremely good at:
- academic papers
- mathematical documents
- research PDFs
- structured scientific layouts

It converts documents directly into:
- markdown-like structure
- semantic text

instead of raw OCR text.

---

# When To Use Nougat

Use Nougat ONLY for:
- research papers
- books
- PDFs with equations
- technical papers

Avoid using it for:
- receipts
- invoices
- handwritten notes
- forms

---

# Smart Routing Layer

The backend should first classify the document.

## Example

```text
if document_type == "research_paper":
    use_nougat()
elif document_type == "scanned_doc":
    use_paddleocr()
elif document_type == "handwritten":
    use_qwen_vl()
```

---

# Proposed Flow

# Flow A — Research Papers

```text
PDF/Image
    ↓
Nougat
    ↓
Markdown/Text
    ↓
Qwen2.5-VL
    ↓
Structured JSON
    ↓
DOCX/PDF
```

## Why This Works

Nougat already understands:
- equations
- sections
- citations
- paper formatting

Qwen then:
- improves hierarchy
- cleans structure
- generates semantic JSON

---

# Flow B — Generic Documents

```text
Image
    ↓
OpenCV
    ↓
PaddleOCR
    ↓
Qwen2.5-VL
    ↓
Structured JSON
    ↓
DOCX/PDF
```

---

# Flow C — Handwritten Notes

```text
Image
    ↓
OpenCV
    ↓
Qwen2.5-VL Direct Vision Parsing
    ↓
Structured JSON
    ↓
DOCX/PDF
```

---

# Project Structure

```text
backend/
│
├── app/
│   ├── api/
│   │   └── routes.py
│   │
│   ├── preprocess/
│   │   └── image_cleaner.py
│   │
│   ├── ocr/
│   │   ├── paddle.py
│   │   └── nougat_parser.py
│   │
│   ├── vlm/
│   │   └── qwen_parser.py
│   │
│   ├── routing/
│   │   └── classifier.py
│   │
│   ├── schemas/
│   │   └── document_schema.py
│   │
│   ├── renderers/
│   │   ├── docx_renderer.py
│   │   └── pdf_renderer.py
│   │
│   └── utils/
│
├── uploads/
├── outputs/
├── temp/
└── models/
```

---

# Universal JSON Schema

Everything should eventually become structured JSON.

## Example

```json
{
  "title": "Machine Learning Notes",
  "sections": [
    {
      "heading": "Introduction",
      "content": [
        {
          "type": "paragraph",
          "text": "Machine learning is..."
        },
        {
          "type": "bullet_list",
          "items": [
            "Supervised Learning",
            "Unsupervised Learning"
          ]
        }
      ]
    }
  ]
}
```

---

# OpenCV Preprocessing

## Goals

Improve OCR quality via:
- grayscale conversion
- denoising
- thresholding
- deskewing
- perspective correction

---

# PaddleOCR Responsibilities

PaddleOCR should provide:
- text
- bounding boxes
- confidence scores

Example output:

```json
[
  {
    "text": "Introduction",
    "bbox": [12, 50, 300, 90],
    "confidence": 0.98
  }
]
```

---

# Qwen2.5-VL Responsibilities

Qwen should:
- infer document hierarchy
- detect headings
- detect paragraphs
- identify tables
- reconstruct reading order
- clean OCR errors
- produce final JSON

---

# Suggested Prompt Strategy

```text
You are a document reconstruction system.

Analyze:
1. Document image
2. OCR text
3. Bounding boxes

Reconstruct:
- title
- sections
- paragraphs
- lists
- tables

Return ONLY valid JSON.
```

---

# DOCX Rendering Strategy

Use:
- python-docx

Responsibilities:
- headings
- paragraph formatting
- bullet lists
- tables
- page breaks

---

# PDF Rendering Strategy

Initially:
DOCX → PDF

Later:
Direct PDF rendering using ReportLab.

---

# Frontend Plan

## Stack

- React
- TailwindCSS
- Axios
- React Query

---

# Frontend Features

## MVP

- Drag/drop upload
- File preview
- Processing status
- Download DOCX/PDF
- Output preview

---

# API Design

## Upload Endpoint

```http
POST /upload
```

Response:

```json
{
  "document_id": "...",
  "status": "processing"
}
```

---

# Parse Endpoint

```http
GET /document/{id}
```

---

# Export Endpoint

```http
GET /export/docx/{id}
GET /export/pdf/{id}
```

---

# Model Choices

## OCR

- PaddleOCR

## Vision LLM

- Qwen2.5-VL-3B
- Qwen2.5-VL-7B

## Scientific Parsing

- Nougat

---

# Hardware Recommendations

## Local Development

| Model | Recommended VRAM |
|---|---|
| Qwen2.5-VL 3B | 8GB |
| Qwen2.5-VL 7B | 16GB |

---

# Phase Roadmap

# Phase 1 — MVP

Goal:
Basic image → DOCX pipeline

### Features

- Upload image
- PaddleOCR extraction
- Qwen JSON structuring
- DOCX export

---

# Phase 2 — Better Layout

### Add

- OpenCV preprocessing
- Bounding-box ordering
- Better paragraph grouping
- Multi-page support

---

# Phase 3 — Nougat Integration

### Add

- Research paper routing
- Markdown parsing
- Equation preservation

---

# Phase 4 — Advanced Features

### Add

- Handwriting support
- Table extraction
- Multilingual support
- RAG indexing
- Semantic search

---

# Long-Term Possibilities

This can evolve into:

- AI note digitizer
- Research paper parser
- Resume editor
- Study assistant
- Legal document processor
- Knowledge extraction engine

---

# Key Insight

OCR extracts text.

Your system reconstructs meaning and structure.

That is the valuable part.