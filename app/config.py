"""
Configuration settings for the Invoice Processor API.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# API Settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# OCR Settings
OCR_LANGUAGES = os.getenv("OCR_LANGUAGES", "eng,ara")
OCR_DPI = int(os.getenv("OCR_DPI", "300"))

# Database Settings
DB_HOST = os.getenv("DB_HOST", "200.1.50.113")
DB_USER = os.getenv("DB_USER", "newuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "renoemgerplive")

# Supported file types
SUPPORTED_IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
SUPPORTED_DOCUMENT_TYPES = {".pdf"}
SUPPORTED_TYPES = SUPPORTED_IMAGE_TYPES | SUPPORTED_DOCUMENT_TYPES

# Max file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# Field mapping defaults
DEFAULT_FIELD_MAPPINGS = {
    # Vendor Details
    "company_name_en": ["Company Name", "Vendor Name", "Supplier Name", "Business Name"],
    "company_name_ar": ["Company Name (Arabic)", "Vendor Name AR", "Supplier Name AR"],
    "address": ["Address", "Vendor Address", "Supplier Address", "Business Address"],
    "head_office_tel": ["Head Office Tel", "Head Office Telephone", "HO Phone", "HO Tel"],
    "head_office_fax": ["Head Office Fax", "HO Fax"],
    "showroom_tel": ["Showroom Tel", "Showroom Telephone", "Showroom Phone"],
    "showroom_fax": ["Showroom Fax"],
    "email": ["Email", "E-mail", "Email Address", "Vendor Email"],
    "tax_registration_number": ["Tax Registration Number", "TRN", "Tax ID", "VAT Number", "Tax No"],
    "excise_registration_number": ["Excise Registration Number", "Excise Reg No", "Excise Number"],

    # Invoice Details
    "invoice_number": ["Invoice Number", "Inv No", "Invoice No", "INV Number", "INV No", "Invoice #"],
    "sales_number": ["Sales No", "Sales Number", "SALES NUMBER"],   
    "invoice_date": ["Invoice Date", "Inv Date", "Date", "Invoice Date"],
    "invoice_type": ["Invoice Type", "Type"],
    "order_number": ["Order Number", "Order No", "PO Number", "Purchase Order"],
    "order_date": ["Order Date", "Order Date"],
    "page_number": ["Page", "Page Number", "Page #"],
    "purchase_order_number": ["Purchase Order Number", "PO Number", "PO No"],
    "lpo_number": ["LPO", "LPO Number"],
    "due_date": ["Due Date", "Payment Due", "Due Date"],
    "payment_terms": ["Payment Terms", "Terms", "Payment Terms"],
    "sales_person": ["Sales Person", "Salesman", "Sales Representative"],
    "supervisor": ["Supervisor", "Manager"],
    "merchandiser": ["Merchandiser", "Merch"],

    # Customer Details
    "customer_code": ["Customer Code", "Customer ID", "Customer No", "Client Code"],
    "customer_name": ["Customer Name", "Client Name", "Bill To Name", "Billing Name"],
    "customer_address": ["Customer Address", "Client Address", "Billing Address"],
    "customer_phone": ["Customer Phone", "Client Phone", "Phone"],
    "customer_email": ["Customer Email", "Client Email"],
    "customer_trn": ["Customer TRN", "Customer Tax ID", "Customer VAT"],
    "customer_vat": ["Customer VAT", "VAT"],

    # Company Details
    "company_name": ["Company Name", "From Name", "Seller Name"],
    "company_street": ["Company Street", "Street"],
    "company_city": ["Company City", "City"],
    "company_state": ["Company State", "State", "Region"],
    "company_zip": ["ZIP", "Zip Code", "Postal Code", "Pin Code"],
    "company_country": ["Country"],
    "company_phone": ["Company Phone", "Phone"],
    "company_email": ["Company Email", "Email"],
    "company_website": ["Website", "Web"],
    "company_tax_id": ["Tax ID", "Tax ID Number"],

    # Bill To
    "bill_to_name": ["Bill To Name", "Bill To"],
    "bill_to_company": ["Bill To Company"],
    "bill_to_street": ["Bill To Street"],
    "bill_to_city": ["Bill To City"],
    "bill_to_state": ["Bill To State"],
    "bill_to_zip": ["Bill To ZIP"],
    "bill_to_country": ["Bill To Country"],
    "bill_to_phone": ["Bill To Phone"],
    "bill_to_email": ["Bill To Email"],
    "bill_to_customer_id": ["Bill To Customer ID"],

    # Ship To
    "ship_to_name": ["Ship To Name", "Ship To", "Ship To Name"],
    "ship_to_company": ["Ship To Company"],
    "ship_to_street": ["Ship To Street"],
    "ship_to_city": ["Ship To City"],
    "ship_to_state": ["Ship To State"],
    "ship_to_zip": ["Ship To ZIP"],
    "ship_to_country": ["Ship To Country"],

    # Line Items
    "line_number": ["Line #", "Line Number", "#"],
    "prod_code": ["Product Code", "Item Code", "SKU", "Code"],
    "barcode": ["Barcode", "Bar Code"],
    "product_name": ["Product Name", "Item Name", "Description", "Item Description", "Particulars"],
    "packing": ["Packing", "Pack"],
    "unit": ["Unit"],
    "unit_of_measure": ["UOM", "Unit of Measure"],
    "manufacturing_date": ["MFG Date", "Manufacturing Date", "MFG"],
    "expiry_date": ["Expiry Date", "EXP"],
    "qty": ["Qty", "Quantity"],
    "quantity": ["Quantity", "Qty","Qty/Case"],
    "list_value": ["List Value", "List Price"],
    "unit_price": ["Unit Price", "Price", "Rate"],
    "gross_amount": ["Gross Amount", "Gross"],
    "discount": ["Discount", "Disc"],
    "discount_percent": ["Discount %", "Discount Percentage", "Discount Percent"],
    "taxed": ["Taxed", "VAT"],
    "amount": ["Amount", "Line Total"], 
    "vat_percent": ["VAT %", "VAT Percent"],
    "net_value": ["Net Value", "Net Amount"],
    "excise_tax": ["Excise", "EXCISE TAX"],
    "total_incl_excise": ["Total Incl Excise"], 
    "vat_amount": ["VAT Amount", "VAT Value"],
    "total_amount": ["Total Amount", "Total Amount AED", "Total Amount (AED)", "Total Incl VAT (AED)", "Grand Total (AED)", "Total Incl VAT", "Grand Total", "Total Due", "Total"],
    

    # Summary
    "subtotal": ["Subtotal", "Sub Total", "Net Amount", "Total Before VAT", "Total Before Excise", "Untaxed Amount", "TOTAL EXCLUDING VAT"],
    "gross_amount": ["TOTAL GROSS AMOUNT", "Gross amount"],
    "discount_total": ["Discount Total", "Total Discount", "Discount Amount", "Disc/Return", "Discount", "Total promotional Discount"],
    "discount_percentage": ["Discount %","Less Discount %","Less Discount % (AED)"],
    "taxable_amount": ["Taxable Value of Supply (AED)"],
    "tax_rate_percent": ["Tax Rate", "VAT Rate", "Tax %", ],
    "vat_total": ["VAT Total", "Total VAT", "VAT Amount", "VAT %", "TOTAL VAT AMOUNT"],
    "shipping": ["Shipping", "Shipping Charges", "Delivery Charges"],
    "other_charges": ["Other Charges", "Miscellaneous", "Misc Charges"],
    "total_amount": ["Total Amount", "Grand Total", "Invoice Total", "Total Due", "NET INVOICE AMOUNT","Total Invoice Value"],
    "amount_paid": ["Amount Paid", "Paid"],
    "balance_due": ["Balance Due", "Balance", "Due Amount"],
    "currency": ["Currency", "Currency Code"],

    # Payment Instructions
    "payable_to": ["Payable To", "Account Name"],
    "payment_method": ["Payment Method", "Payment Mode", "Mode of Payment"],
    "bank_name": ["Bank Name", "Bank"],
    "account_name": ["Account Name", "A/C Name", "A/C"],
    "account_number": ["Account Number", "A/C No", "Account No"],
    "ifsc_swift": ["IFSC", "SWIFT", "SWIFT Code", "IFSC Code"],

    # Footer
    "total_discount": ["Total Discount"],
    "total_net_inv_value": ["Total Net Invoice Value", "Net Invoice Value"],
    "list_value_total": ["List Value Total"],
    "total_excise": ["Total Excise"],
    "total_incl_excise": ["Total Incl Excise", "Supplied Inluding Excise"],
    "total_vat_aed": ["Total VAT AED", "Total VAT"],
    "round_off": ["Round Off","Roundoff","Round Off (AED)","Roundoff (AED)"],
    "total_incl_vat_aed": ["Total Incl VAT AED", "TOTAL WITH VAT"],
    "amount_in_words": ["Amount in Words", "Amount in Word"],
    "rebate_note": ["Rebate Note"],
    "return_policy": ["Return Policy"],
    "delivery_remarks": ["Delivery Remarks"],
    "prepared_by": ["Prepared By"],
    "printed_by": ["Printed By"],
    "print_timestamp": ["Print Timestamp", "Printed On"],
    "warehouse_loc": ["Warehouse", "Warehouse Location"],
}
