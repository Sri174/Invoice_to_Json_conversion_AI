"""
Main Invoice Processing Service.
"""
import os
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import shutil

from fastapi import UploadFile, HTTPException
from app.gemini_processor import GeminiProcessor
from app.config import UPLOAD_DIR, SUPPORTED_TYPES, MAX_FILE_SIZE
from app.schema import get_invoice_schema

logger = logging.getLogger(__name__)


class InvoiceProcessor:
    """Main service for processing invoices."""

    def __init__(self):
        self.gemini = GeminiProcessor()
        self.upload_dir = UPLOAD_DIR
        self.upload_dir.mkdir(exist_ok=True)

    async def process_invoice(
        self,
        file: UploadFile,
            custom_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process an invoice file and return structured JSON using Gemini.

        Args:
            file: Uploaded file (PDF or image)
            custom_text: Optional pre-extracted text or additional context

        Returns:
            Structured invoice data matching the schema
        """
        # Validate file
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")

        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in SUPPORTED_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Supported: {', '.join(SUPPORTED_TYPES)}"
            )

        # Generate unique session ID
        session_id = str(uuid.uuid4())
        session_dir = self.upload_dir / session_id
        session_dir.mkdir(exist_ok=True)

        file_path = None
        image_paths = []

        try:
            # Save uploaded file
            file_path = session_dir / file.filename
            with open(file_path, "wb") as buffer:
                content = await file.read()
                if len(content) > MAX_FILE_SIZE:
                    raise HTTPException(status_code=413, detail="File too large (max 10MB)")
                buffer.write(content)

            logger.info(f"Processing file: {file.filename} (session: {session_id})")

            # Process with Gemini
            result = await self.gemini.process_document(str(file_path), custom_text)

            # Add processing metadata
            result["_metadata"] = {
                "session_id": session_id,
                "source_file": file.filename,
                "file_type": file_ext
            }

            return result

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing invoice: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
        finally:
            # Maintain a maximum of 10 session directories as requested
            self._cleanup_old_uploads()

    def _cleanup_old_uploads(self):
        """Keep only the latest 10 session directories in the uploads folder."""
        try:
            # Get all subdirectories in upload_dir
            directories = [d for d in self.upload_dir.iterdir() if d.is_dir()]
            # Sort by creation/modification time (oldest first)
            directories.sort(key=lambda x: x.stat().st_mtime)
            
            # If we have more than 10, delete the oldest ones
            if len(directories) > 10:
                dirs_to_delete = directories[:-10]
                for d in dirs_to_delete:
                    shutil.rmtree(d, ignore_errors=True)
                    logger.info(f"Cleaned up old session directory: {d.name}")
        except Exception as e:
            logger.warning(f"Failed to cleanup old uploads: {str(e)}")

    def process_text_only(
        self,
        text: str,
        field_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Process already extracted text.

        Args:
            text: The extracted text
            field_mapping: Optional custom field mapping

        Returns:
            Structured invoice data matching the schema
        """
        raise NotImplementedError("Text-only processing without a file is deprecated in Gemini pipeline.")

    def get_schema(self) -> Dict[str, Any]:
        """Return the invoice schema structure."""
        return get_invoice_schema()
