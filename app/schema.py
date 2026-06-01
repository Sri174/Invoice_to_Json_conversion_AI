"""
JSON Schema for invoice extraction response.
This defines the exact structure returned by the API.
"""

def get_invoice_schema():
    """Returns the invoice JSON schema structure."""
    return {
        "document_type": "",
        "header": {
            "vendor_details": {
                "company_name_en": "",
                "company_name_ar": "",
                "address": "",
                "phone": "",
                "contact_info": {
                    "head_office_tel": "",
                    "head_office_fax": "",
                    "showroom_tel": "",
                    "showroom_fax": "",
                    "email": ""
                },
                "tax_registration_number": "",
                "excise_registration_number": ""
            },
            "invoice_details": {
                "invoice_number": "",
                "sales_number": "",
                "invoice_date": "",
                "invoice_type": "",
                "order_number": "",
                "order_date": "",
                "page_number": "",
                "purchase_order_number": "",
                "due_date": "",
                "payment_terms": "",
                "personnel": {
                    "sales_person": "",
                    "supervisor": "",
                    "merchandiser": ""
                }
            },
            "customer_details": {
                "customer_code": "",
                "company": "",
                "name": "",
                "address": "",
                "phone": "",
                "email": "",
                "trn": "",
                "customer_vat": ""
            }
        },
        "ship_to": {
            "name": "",
            "company": "",
            "address": {
                "street": "",
                "city": "",
                "state": "",
                "zip": "",
                "country": ""
            }
        },
        "line_items": [
            {
                "line_number": None,
                "prod_code": "",
                "barcode": "",
                "product_name": "",
                "description": "",
                "packing": "",
                "unit": "",
                "expiry_date": "",
                "quantity": None,
                "unit_price": None,
                "discount": None,
                "discount_percent": None,
                "taxed": False,
                "vat_percent": None,
                "excise": None,
                "total_incl_excise": None,
                "vat_amount": None,
                "amount": None,
                
            }
        ],
        "summary": {
            "subtotal": None,
            "gross_amount": None,
            "discount_total": None,
            "discount_percentage": None,
            "taxable_amount": None,
            "tax_rate_percent": None,
            "vat_total": None,
            "shipping": None,
            "other_charges": None,
            "total_amount": None,
            "amount_paid": None,
            "balance_due": None,
            "currency": ""
        },
        "payment_instructions": {
            "payable_to": "",
            "payment_method": "",
            "bank_details": {
                "bank_name": "",
                "account_name": "",
                "account_number": "",
                "ifsc_swift": ""
            },
            "notes": []
        },
        "codes": [
            {
                "type": "",
                "value": "",
                "confidence": 1.0
            }
        ],
        "footer": {
            "totals_summary": {
                "total_discount": None,
                "total_net_inv_value": None,
                "total_excise": None,
                "total_incl_excise": None,
                "total_vat_aed": None,
                "round_off":None,
                "total_incl_vat_aed": None,
                "amount_in_words": ""
            },
            "remarks_and_notes": {
                "rebate_note": "",
                "payment_terms": "",
                "return_policy": "",
                "delivery_remarks": ""
            },
            "processing_info": {
                "prepared_by": "",
                "printed_by": "",
                "print_timestamp": "",
                "warehouse_loc": ""
            },
            "notes": [],
            "thank_you_note": ""
        }
    }
