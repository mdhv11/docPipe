from fastapi import FastAPI
from dotenv import load_dotenv

from app.api.routes import router
from app.utils.paths import ensure_directories

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="docPipe AI Document Reconstruction",
    description="A minimal backend for document OCR + semantic reconstruction using llama.cpp.",
    version="0.1.0",
)

app.include_router(router)

ensure_directories()
