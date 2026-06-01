"""
Test script to verify the Invoice Processor API installation.
"""
import sys
import os

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        from app.config import DEFAULT_FIELD_MAPPINGS
        print("✓ app.config imported")
    except ImportError as e:
        print(f"✗ app.config import failed: {e}")
        return False

    try:
        from app.schema import get_invoice_schema
        print("✓ app.schema imported")
    except ImportError as e:
        print(f"✗ app.schema import failed: {e}")
        return False

    try:
        from app.field_mapper import FieldMapper
        print("✓ app.field_mapper imported")
    except ImportError as e:
        print(f"✗ app.field_mapper import failed: {e}")
        return False

    try:
        from app.service import InvoiceProcessor
        print("✓ app.service imported")
    except ImportError as e:
        print(f"✗ app.service import failed: {e}")
        return False

    return True

def test_tesseract():
    """Test Tesseract OCR availability."""
    print("\nTesting Tesseract OCR...")

    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract version: {version}")
        return True
    except Exception as e:
        print(f"✗ Tesseract not available: {e}")
        print("  Install from: https://github.com/UB-Mannheim/tesseract/wiki")
        return False

def test_pymupdf():
    """Test PyMuPDF availability."""
    print("\nTesting PyMuPDF...")

    try:
        import fitz
        print(f"✓ PyMuPDF version: {fitz.version}")
        return True
    except ImportError as e:
        print(f"✗ PyMuPDF import failed: {e}")
        return False

def test_field_mapper():
    """Test the field mapper with sample text."""
    print("\nTesting field mapper...")

    from app.field_mapper import FieldMapper

    sample_text = """
    INVOICE

    Invoice Number: INV-2024-001
    Invoice Date: 2024-01-15
    Due Date: 2024-02-15

    Bill To: ABC Company
    Address: Dubai, UAE
    TRN: 123456789

    Description          Qty    Unit Price    Amount
    Office Chair          10      150.00      1500.00
    Office Desk            5      300.00      1500.00

    Subtotal: 3000.00
    VAT (5%): 150.00
    Total: 3150.00

    Thank you for your business!
    """

    mapper = FieldMapper()
    result = mapper.map_to_schema(sample_text)

    # Verify schema structure
    required_sections = ['header', 'document_type', 'line_items', 'summary']
    for section in required_sections:
        if section in result:
            print(f"✓ Schema section '{section}' present")
        else:
            print(f"✗ Schema section '{section}' missing")
            return False

    # Verify line items
    if len(result['line_items']) > 0:
        print(f"✓ Found {len(result['line_items'])} line item(s)")
    else:
        print("⚠ No line items extracted (may need adjustment)")

    # Verify summary values
    if result['summary'].get('total_amount'):
        print(f"✓ Total amount extracted: {result['summary']['total_amount']}")

    return True

def main():
    print("=" * 50)
    print("Invoice Processor API - Installation Test")
    print("=" * 50)

    all_passed = True

    if not test_imports():
        all_passed = False

    if not test_pymupdf():
        all_passed = False

    if not test_tesseract():
        print("⚠ Tesseract not installed (OCR will not work)")
        print("  This is optional but required for image processing")

    if not test_field_mapper():
        all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All tests passed!")
        print("\nTo start the API:")
        print("  python run.py")
        print("\nOr:")
        print("  uvicorn app.main:app --reload")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
