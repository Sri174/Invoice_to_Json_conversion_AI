"""
Client examples for Invoice Processor API
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"


def example_1_process_file():
    """Process an invoice file with field mapping."""
    print("\n" + "=" * 60)
    print("Example 1: Process Invoice File")
    print("=" * 60)

    url = f"{BASE_URL}/process"

    # Define field mapping
    field_mapping = {
        "invoice_number": "INV no",
        "invoice_date": "Invoice Date",
        "customer_name": "Bill To",
        "total_amount": "Grand Total"
    }

    # Prepare the files and data
    files = {
        'file': open('sample_invoice.pdf', 'rb')
    }
    data = {
        'field_mapping': json.dumps(field_mapping),
        'language': 'eng'
    }

    # Make request
    response = requests.post(url, files=files, data=data)
    result = response.json()

    print(f"Status: {response.status_code}")
    print(f"Invoice Number: {result.get('header', {}).get('invoice_details', {}).get('invoice_number')}")
    print(f"Total Amount: {result.get('summary', {}).get('total_amount')}")
    print(f"Line Items: {len(result.get('line_items', []))}")

    return result


def example_2_process_text():
    """Process extracted text with field mapping."""
    print("\n" + "=" * 60)
    print("Example 2: Process Extracted Text")
    print("=" * 60)

    url = f"{BASE_URL}/process/text"

    # Sample extracted text from OCR
    sample_text = """
    TAX INVOICE

    Invoice No: INV-2024-001
    Date: 15-Jan-2024
    Due Date: 15-Feb-2024

    From: ABC Supplies LLC
    Address: Dubai, UAE
    Email: info@abcsupplies.com
    TRN: 123456789

    Bill To: XYZ Company
    Address: Abu Dhabi, UAE
    TRN: 987654321

    Description       Qty    Rate     Amount
    Office Chair       10   150.00   1500.00
    Office Desk         5   300.00   1500.00
    Meeting Table       2   500.00   1000.00

    Subtotal: 4000.00
    Discount: 200.00
    Taxable Amount: 3800.00
    VAT (5%): 190.00
    Shipping: 50.00
    Total: 4040.00

    Amount Paid: 4040.00
    Balance Due: 0.00

    Thank you for your business!
    """

    field_mapping = {
        "invoice_number": "Invoice No",
        "invoice_date": "Date",
        "due_date": "Due Date",
        "company_name_en": "From",
        "customer_name": "Bill To",
        "subtotal": "Subtotal",
        "discount_total": "Discount",
        "taxable_amount": "Taxable Amount",
        "vat_total": "VAT (5%)",
        "shipping": "Shipping",
        "total_amount": "Total",
        "amount_paid": "Amount Paid",
        "balance_due": "Balance Due"
    }

    payload = {
        "text": sample_text,
        "field_mapping": field_mapping
    }

    response = requests.post(url, json=payload)
    result = response.json()

    print(f"Status: {response.status_code}")
    print(f"Invoice Number: {result.get('header', {}).get('invoice_details', {}).get('invoice_number')}")
    print(f"Customer: {result.get('header', {}).get('customer_details', {}).get('name')}")
    print(f"Subtotal: {result.get('summary', {}).get('subtotal')}")
    print(f"VAT Total: {result.get('summary', {}).get('vat_total')}")
    print(f"Total Amount: {result.get('summary', {}).get('total_amount')}")
    print(f"Currency: {result.get('summary', {}).get('currency')}")
    print(f"Line Items: {len(result.get('line_items', []))}")

    return result


def example_3_preview_extraction():
    """Preview raw OCR extraction without mapping."""
    print("\n" + "=" * 60)
    print("Example 3: Preview OCR Extraction")
    print("=" * 60)

    url = f"{BASE_URL}/preview-extraction"

    files = {'file': open('sample_invoice.pdf', 'rb')}
    data = {'language': 'eng'}

    response = requests.post(url, files=files, data=data)
    result = response.json()

    print(f"Status: {response.status_code}")
    print(f"Text Length: {result.get('text_length')}")
    print(f"\nPreview (first 500 chars):\n{result.get('text_preview', '')[:500]}")

    return result


def example_4_batch_process():
    """Process multiple invoices."""
    print("\n" + "=" * 60)
    print("Example 4: Batch Process")
    print("=" * 60)

    url = f"{BASE_URL}/batch-process"

    # Process all PDFs in current directory
    files = []
    for pdf_file in Path('.').glob('*.pdf'):
        files.append(('files', (pdf_file.name, open(pdf_file, 'rb'), 'application/pdf')))

    if not files:
        print("No PDF files found in current directory")
        return

    field_mapping = {
        "invoice_number": "Invoice No",
        "total_amount": "Total"
    }
    data = {
        'field_mapping': json.dumps(field_mapping),
        'language': 'eng'
    }

    response = requests.post(url, files=files, data=data)
    result = response.json()

    print(f"Total Files: {result.get('total')}")
    print(f"Successful: {result.get('successful')}")
    print(f"Failed: {result.get('failed')}")

    for r in result.get('results', []):
        print(f"  - {r.get('filename')}: {'OK' if r.get('success') else r.get('error')}")

    # Close file handles
    for _, f in files:
        f[1].close()

    return result


def example_5_get_schema():
    """Get the invoice JSON schema."""
    print("\n" + "=" * 60)
    print("Example 5: Get Invoice Schema")
    print("=" * 60)

    url = f"{BASE_URL}/schema"
    response = requests.get(url)
    schema = response.json()

    print(f"Schema Keys: {list(schema.keys())}")
    print(f"Header Keys: {list(schema.get('header', {}).keys())}")
    print(f"Line Items: {len(schema.get('line_items', []))} item template")
    print(f"Summary Keys: {list(schema.get('summary', {}).keys())}")

    return schema


def example_6_validate_mapping():
    """Validate field mapping configuration."""
    print("\n" + "=" * 60)
    print("Example 6: Validate Field Mapping")
    print("=" * 60)

    url = f"{BASE_URL}/validate-mapping"

    mapping = {
        "invoice_number": "INV no",
        "invoice_date": "Date",
        "customer_name": "Bill To",
        "total_amount": "Grand Total"
    }

    response = requests.post(url, json={"mapping": mapping})
    result = response.json()

    print(f"Valid: {result.get('valid')}")
    print(f"Mapping Count: {result.get('mapping_count')}")
    print(f"Covered Fields: {result.get('covered_fields')}")

    return result


def main():
    """Run all examples."""
    print("Invoice Processor API - Client Examples")
    print("Make sure the API is running on", BASE_URL)

    try:
        # Check health first
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print(f"API not healthy: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print(f"Cannot connect to API at {BASE_URL}")
        print("Start the API with: python run.py")
        return

    # Run examples
    example_5_get_schema()
    example_6_validate_mapping()
    example_2_process_text()

    # Uncomment to run file-based examples (requires actual files)
    # example_1_process_file()
    # example_3_preview_extraction()
    # example_4_batch_process()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
