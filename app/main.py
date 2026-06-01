"""
Invoice Processor API - FastAPI Application
"""
import os
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
import logging
from typing import Optional, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.service import InvoiceProcessor
from app.schema import get_invoice_schema

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Invoice Processor API starting up...")
    yield
    logger.info("Invoice Processor API shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Invoice Processor API",
    description="OCR-based invoice extraction API with field mapping support",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processor
processor = InvoiceProcessor()


# Request/Response models
class TextProcessRequest(BaseModel):
    """Request model for text-only processing (Deprecated)."""
    text: str


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "invoice-processor"}


# Schema endpoint
@app.get("/schema")
async def get_schema():
    """Return the invoice JSON schema structure."""
    return processor.get_schema()


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Invoice Processor API",
        "version": "1.0.0",
        "endpoints": {
            "POST /process": "Process invoice file (multipart/form-data)",
            "GET /schema": "Get invoice JSON schema",
            "GET /health": "Health check"
        }
    }


# File processing endpoint
@app.post("/process")
async def process_invoice(
    file: UploadFile = File(..., description="Invoice file (PDF or image)"),
    custom_text: Optional[str] = Form(None, description="Additional text to include")
):
    """
    Process an invoice file and extract structured data using Gemini.

    **File:** PDF or image file (jpg, png, bmp, tiff, webp)

    **Custom Text (optional):** Additional text to include in processing as context for Gemini.
    """
    try:
        result = await processor.process_invoice(
            file=file,
            custom_text=custom_text
        )

        return JSONResponse(content=result)

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in process_invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



# Include additional routes
from app.routes import router as additional_router
app.include_router(additional_router)


# Run with uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
