"""
Additional API routes for batch processing and utilities.
"""
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import json

router = APIRouter()


@router.post("/batch-process")
async def batch_process_invoices(
    files: List[UploadFile] = File(..., description="Multiple invoice files"),
    field_mapping: Optional[str] = Form(None, description="JSON string of field mapping"),
    language: Optional[str] = Form("eng", description="OCR language")
):
    """
    Process multiple invoice files in batch.

    Returns a list of results, one per file.
    """
    from app.main import processor

    mapping = None
    if field_mapping:
        try:
            mapping = json.loads(field_mapping)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid field_mapping JSON")

    results = []
    for file in files:
        try:
            result = await processor.process_invoice(
                file=file,
                field_mapping=mapping,
                language=language
            )
            results.append({
                "filename": file.filename,
                "success": True,
                "data": result
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })

    return JSONResponse(content={
        "total": len(files),
        "successful": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
        "results": results
    })


@router.get("/supported-formats")
async def get_supported_formats():
    """Return supported file formats and their types."""
    return {
        "images": [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"],
        "documents": [".pdf"],
        "max_file_size_mb": 10
    }


@router.get("/field-mappings/default")
async def get_default_field_mappings():
    """Return the default field mappings from DB or fallback to config."""
    from app.config import DEFAULT_FIELD_MAPPINGS
    from app.db import get_settings_mapping
    
    db_mapping = get_settings_mapping()
    if db_mapping:
        db_mapping["_source_info"] = "Loaded dynamically from mst_settingsocr"
        return db_mapping
        
    fallback = DEFAULT_FIELD_MAPPINGS.copy()
    fallback["_source_info"] = "Database connection failed or settingsvalue was empty. Using local fallback."
    return fallback


@router.post("/preview-extraction")
async def preview_extraction(
    file: UploadFile = File(...),
    language: Optional[str] = Form("eng")
):
    """
    Preview raw OCR extraction without field mapping.
    Useful for debugging and tuning field mappings.
    """
    from app.main import processor
    import tempfile
    from pathlib import Path

    try:
        # Save file temporarily
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Process based on file type
        if suffix.lower() == ".pdf":
            from app.pdf_processor import PDFProcessor
            pdf = PDFProcessor()
            text = pdf.extract_text_from_pdf(tmp_path)
            if not text.strip():
                images = pdf.pdf_to_images(tmp_path)
                for img in images:
                    from app.ocr_processor import OCRProcessor
                    ocr = OCRProcessor()
                    text += ocr.extract_text_from_image(img)
        else:
            from app.ocr_processor import OCRProcessor
            ocr = OCRProcessor()
            text = ocr.extract_text_from_image(tmp_path)

        # Clean up
        Path(tmp_path).unlink()

        return JSONResponse(content={
            "filename": file.filename,
            "text_length": len(text),
            "text_preview": text[:2000],  # First 2000 chars
            "full_text": text
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
