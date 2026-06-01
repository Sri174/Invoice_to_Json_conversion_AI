import os
import json
import logging
import urllib.request
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

def get_settings_mapping() -> Optional[Dict[str, Any]]:
    """
    Fetch the OCR settings mapping from the team's internal API endpoint.
    Returns the parsed JSON dictionary, or None if empty/failed.
    """
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    # Defaults provided by the team
    company_id = int(os.getenv("OCR_COMPANY_ID", "27"))
    settings_ocr_id = int(os.getenv("OCR_SETTINGS_ID", "0"))
    api_url = os.getenv("OCR_SETTINGS_API_URL", "http://200.1.50.10:7003/settings/getsettingsocr")
    
    try:
        # Prepare the POST request body
        body = json.dumps({
            "settingsocrid": settings_ocr_id,
            "companyid": company_id
        }).encode('utf-8')
        
        req = urllib.request.Request(
            api_url, 
            data=body, 
            headers={'Content-Type': 'application/json'}, 
            method='POST'
        )
        
        # Send the request
        with urllib.request.urlopen(req, timeout=10) as response:
            response_data = response.read().decode('utf-8')
            parsed_response = json.loads(response_data)
            
            # The API returns {"result": [ [rows], {metadata} ] }
            result_list = parsed_response.get("result")
            if isinstance(result_list, list) and len(result_list) > 0:
                rows = result_list[0]
                
                # Build the mapping dictionary
                mapping = {}
                for row in rows:
                    if not row.get("inactive") and row.get("settingsvalue"):
                        try:
                            # settingsvalue is a JSON string of a list
                            values_list = json.loads(row["settingsvalue"])
                            mapping[row["settingsocrname"]] = values_list
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse settingsvalue for {row.get('settingsocrname')}")
                            
                if mapping:
                    return mapping
                    
            return None
            
    except Exception as e:
        logger.error(f"Error querying settings API ({api_url}): {str(e)}")
        return None
