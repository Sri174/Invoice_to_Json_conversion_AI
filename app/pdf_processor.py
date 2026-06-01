"""
PDF Processing module.
"""
import logging
import os
from pathlib import Path
from typing import List, Tuple
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handles PDF processing and conversion to images."""

    def __init__(self):
        self.dpi = 300
        self.zoom_factor = 2.0  # Higher quality

    def pdf_to_images(self, pdf_path: str, output_dir: str = None) -> List[str]:
        """
        Convert PDF pages to images.

        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save images (default: same directory as PDF)

        Returns:
            List of paths to generated images
        """
        try:
            pdf_document = fitz.open(pdf_path)
            image_paths = []

            if output_dir is None:
                output_dir = os.path.dirname(pdf_path)

            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                # Calculate zoom for desired DPI
                zoom = self.zoom_factor
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)

                output_path = os.path.join(
                    output_dir,
                    f"{Path(pdf_path).stem}_page_{page_num + 1}.png"
                )
                pix.save(output_path)
                image_paths.append(output_path)
                logger.info(f"Converted page {page_num + 1} to {output_path}")

            pdf_document.close()
            return image_paths

        except Exception as e:
            logger.error(f"Error converting PDF to images: {str(e)}")
            raise

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text directly from PDF (for searchable PDFs).

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text
        """
        try:
            pdf_document = fitz.open(pdf_path)
            text_parts = []

            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                text_parts.append(page.get_text())

            pdf_document.close()
            return '\n\n'.join(text_parts)

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def get_page_count(self, pdf_path: str) -> int:
        """Get the number of pages in a PDF."""
        try:
            pdf_document = fitz.open(pdf_path)
            count = len(pdf_document)
            pdf_document.close()
            return count
        except Exception as e:
            logger.error(f"Error getting page count: {str(e)}")
            return 0
