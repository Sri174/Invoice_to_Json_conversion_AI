# Invoice Processor API

A Python-based REST API that extracts structured data from invoice images and PDFs using OCR, with support for custom field mapping.

## Features

- **Multi-format Support**: Process PDF documents and images (JPG, PNG, BMP, TIFF, WEBP)
- **OCR Processing**: Uses Tesseract OCR for text extraction with support for multiple languages
- **Field Mapping**: Define custom field mappings to match your invoice format
- **Bilingual Support**: Handle both English and Arabic invoices
- **Structured Output**: Always returns JSON in the same schema format
- **Batch Processing**: Process multiple invoices at once

## Prerequisites

1. **Python 3.10+**
2. **Tesseract OCR**
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - For Windows: Install and add to PATH
   - For Arabic support: Install Arabic language data during installation

## Installation

```bash
# Clone or navigate to the project directory
cd invoice_processor

# Install Python dependencies
pip install -r requirements.txt

# Verify Tesseract installation
tesseract --version
```

## Quick Start

```bash
# Run the API
python run.py

# Or directly with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Access the API at: http://localhost:8000
API Documentation: http://localhost:8000/docs

## API Endpoints

### POST /process
Process an invoice file (PDF or image)

```bash
curl -X POST "http://localhost:8000/process" \
  -F "file=@invoice.pdf" \
  -F 'field_mapping={"invoice_number": "INV no", "invoice_date": "Date"}' \
  -F "language=eng"
```

### POST /process/text
Process already extracted text

```bash
curl -X POST "http://localhost:8000/process/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Invoice No: 12345\nDate: 2024-01-15\nTotal: $500",
    "field_mapping": {"invoice_number": "Invoice No", "total_amount": "Total"}
  }'
```

### GET /schema
Get the invoice JSON schema structure

```bash
curl http://localhost:8000/schema
```

### POST /preview-extraction
Preview raw OCR text without field mapping

```bash
curl -X POST "http://localhost:8000/preview-extraction" \
  -F "file=@invoice.pdf"
```

## Field Mapping

The field mapping allows you to define how custom field names in your invoices map to the standard schema.

**Format**: `{"schema_field": "invoice_field_name"}`

Example mapping:
```json
{
  "invoice_number": "INV no",
  "invoice_date": "Invoice Date",
  "total_amount": "Grand Total",
  "customer_name": "Bill To"
}
```

### Supported Schema Fields

**Header Section:**
- `company_name_en`, `company_name_ar`, `address`, `email`
- `head_office_tel`, `head_office_fax`, `showroom_tel`, `showroom_fax`
- `tax_registration_number`, `excise_registration_number`

**Invoice Details:**
- `invoice_number`, `invoice_date`, `invoice_type`
- `order_number`, `order_date`, `purchase_order_number`
- `due_date`, `payment_terms`
- `sales_person`, `supervisor`, `merchandiser`

**Customer Details:**
- `customer_code`, `customer_name`, `customer_address`
- `customer_phone`, `customer_email`, `customer_trn`

**Line Items:**
- `line_number`, `prod_code`, `barcode`
- `product_name`, `description`, `packing`
- `qty`, `quantity`, `unit_price`
- `discount`, `vat_percent`, `net_value`
- `amount`

**Summary:**
- `subtotal`, `discount_total`, `taxable_amount`
- `tax_rate_percent`, `vat_total`
- `shipping`, `other_charges`
- `total_amount`, `amount_paid`, `balance_due`
- `currency`

## Example Response

```json
{
  "header": {
    "vendor_details": {
      "company_name_en": "ABC Supplies LLC",
      "address": "Dubai, UAE",
      "contact_info": {
        "email": "sales@abcsupplies.com"
      },
      "tax_registration_number": "12345678"
    },
    "invoice_details": {
      "invoice_number": "INV-2024-001",
      "invoice_date": "2024-01-15"
    },
    "customer_details": {
      "name": "XYZ Company",
      "trn": "87654321"
    }
  },
  "document_type": "invoice",
  "line_items": [
    {
      "line_number": 1,
      "product_name": "Office Chair",
      "qty": 10,
      "unit_price": 150.00,
      "amount": 1500.00
    }
  ],
  "summary": {
    "subtotal": 1500.00,
    "vat_total": 150.00,
    "total_amount": 1650.00,
    "currency": "AED"
  }
}
```

## Project Structure

```
invoice_processor/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration and field mappings
│   ├── schema.py          # JSON schema definition
│   ├── main.py            # FastAPI application
│   ├── routes.py          # Additional API routes
│   ├── service.py         # Main processing service
│   ├── ocr_processor.py   # OCR text extraction
│   ├── pdf_processor.py   # PDF handling
│   └── field_mapper.py    # Field mapping logic
├── uploads/               # Temporary file storage
├── requirements.txt
├── run.py                 # Startup script
└── README.md
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| API_HOST | 0.0.0.0 | Server host |
| API_PORT | 8000 | Server port |
| DEBUG | true | Debug mode |
| OCR_LANGUAGES | eng,ara | OCR languages |
| OCR_DPI | 300 | Image DPI for OCR |
| TESSERACT_PATH | (system) | Tesseract executable path |

## License

MIT
