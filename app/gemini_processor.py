import os
import json
import logging
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from app.schema import get_invoice_schema

logger = logging.getLogger(__name__)

class GeminiProcessor:
    """Handles extracting invoice data natively from PDF or image using Gemini."""
    
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        # Configure Gemini API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("GOOGLE_API_KEY not found in environment. Gemini processing may fail.")
        
        self.client = genai.Client(api_key=api_key)
        
        # Using the latest lite model supported by google-genai
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
        
    def _get_extraction_prompt(self, custom_text: Optional[str] = None) -> str:
        """Construct the prompt to instruct Gemini on how to extract the data."""
        schema = get_invoice_schema()
        schema_json = json.dumps(schema, indent=2)
        
        prompt = (
            "You are an expert AI extraction system specifically designed to parse invoices and receipts. "
            "Your task is to carefully analyze the provided document (which may be an image or a multi-page PDF invoice) "
            "and extract all relevant information to perfectly match the following JSON schema.\n\n"
            "JSON Schema you must conform to:\n"
            f"{schema_json}\n\n"
        )
        
        # Inject the dynamic field mappings from the database (or config fallback)
        from app.routes import get_default_field_mappings
        import asyncio
        
        # We need to run it synchronously or just fetch it via the db directly
        from app.db import get_settings_mapping
        from app.config import DEFAULT_FIELD_MAPPINGS
        
        db_mapping = get_settings_mapping()
        if db_mapping:
            logger.info("Fetching dynamic field mappings from DB for /process endpoint...")
            mapping = db_mapping
        else:
            logger.info("Using default fallback field mappings for /process endpoint...")
            mapping = DEFAULT_FIELD_MAPPINGS
            
        mapping_json = json.dumps(mapping, indent=2)
        
        prompt += (
            "FIELD MAPPING DICTIONARY:\n"
            "Below is a dictionary mapping the JSON Schema keys to the exact labels you might see printed on the document.\n"
            "Use these mappings to correctly identify which printed values belong to which JSON keys:\n"
            f"{mapping_json}\n\n"
        )

        prompt += (
            "INSTRUCTIONS:\n"
            "1. Extract the data thoroughly and accurately. Do not invent any information; if a field is not present in the document, leave it as null or an empty string according to the schema's default types.\n"
            "2. Pay special attention to line items. If there are multiple pages, make sure to aggregate all line items across all pages.\n"
            "3. For the `line_items` array, you MUST automatically assign a sequential `line_number` starting from 1 (1, 2, 3...) for each row, even if the source document doesn't explicitly have line numbers.\n"
            "4. Ensure all numeric amounts (totals, taxes, line item prices) are parsed as numbers (float), without currency symbols or commas.\n"
            "5. CRITICAL: When extracting `subtotal`, `taxable_amount`, or `total_amount`, the invoice might have a total quantity listed on the same row. DO NOT extract the total quantity as the monetary value. The monetary value is ALWAYS the right-most number on that row. (e.g. if the line says 'Sub Total (AED) 20.00 607.23', the subtotal is 607.23, NOT 20.00).\n"
            "6. If a percentage is written inline with a label (e.g., 'Vat 5% 4.80'), extract the percentage (5.0) into `tax_rate_percent` or `vat_percent`, and the monetary amount (4.80) into `vat_total` or `vat_amount`.\n"
            "7. Return ONLY a valid, fully parsable JSON object. Do not include any markdown formatting (like ```json), no explanations, no greetings, and absolutely NO trailing text.\n"
            "8. For the `quantity` field, if the quantity is listed under 'Qty/Case' or similar in a fractional format like '0/4' or '2/0', intelligently extract the actual quantity number (e.g., '0/4' means quantity is 4, '2/0' means quantity is 2). Do not output the slash string, only output the resolved numeric quantity.\n"
        )
        
        if custom_text:
            prompt += (
                f"\n\nADDITIONAL CONTEXT FROM USER:\n"
                f"{custom_text}\n"
                "Please consider this context when extracting data."
            )
            
        return prompt

    async def process_document(self, file_path: str, custom_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload the document to Gemini and ask it to extract the structured data.
        """
        uploaded_file = None
        try:
            logger.info(f"Uploading file {file_path} to Gemini...")
            # Upload the file to Gemini's File API
            uploaded_file = self.client.files.upload(file=file_path)
            
            logger.info(f"File uploaded successfully. Generating content with {self.model_name}...")
            
            prompt = self._get_extraction_prompt(custom_text)
            
            import asyncio
            max_retries = 3
            base_wait = 4
            response = None
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"Generating content with {self.model_name} (Attempt {attempt + 1})...")
                    # Run synchronous genai API call in a separate thread to prevent blocking event loop
                    response = await asyncio.to_thread(
                        self.client.models.generate_content,
                        model=self.model_name,
                        contents=[uploaded_file, prompt],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.0
                        )
                    )
                    break
                except Exception as e:
                    error_msg = str(e).lower()
                    if "503" in error_msg or "429" in error_msg or "unavailable" in error_msg:
                        if attempt < max_retries - 1:
                            wait_time = base_wait * (2 ** attempt)
                            logger.warning(f"Gemini API busy: {e}. Retrying in {wait_time}s...")
                            await asyncio.sleep(wait_time)
                            continue
                    raise e
            
            result_text = response.text
            
            # Log token usage
            if response.usage_metadata:
                logger.info(
                    f"Gemini Token Usage: {response.usage_metadata.model_dump_json() if hasattr(response.usage_metadata, 'model_dump_json') else response.usage_metadata}"
                )
            
            # Safely parse JSON
            try:
                parsed_json = json.loads(result_text)
                return parsed_json
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini output as JSON: {result_text}")
                # Fallback clean-up just in case
                clean_text = result_text.strip()
                if clean_text.startswith("```json"):
                    clean_text = clean_text[7:]
                if clean_text.startswith("```"):
                    clean_text = clean_text[3:]
                if clean_text.endswith("```"):
                    clean_text = clean_text[:-3]
                
                # Extremely aggressive cleanup: find first { and last }
                start_idx = clean_text.find('{')
                end_idx = clean_text.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    clean_text = clean_text[start_idx:end_idx+1]
                
                return json.loads(clean_text)
                
        except Exception as e:
            logger.error(f"Error during Gemini processing: {str(e)}")
            raise e
        finally:
            if uploaded_file:
                logger.info("Cleaning up uploaded file from Gemini...")
                try:
                    self.client.files.delete(name=uploaded_file.name)
                except Exception as e:
                    logger.warning(f"Failed to delete file from Gemini: {e}")
