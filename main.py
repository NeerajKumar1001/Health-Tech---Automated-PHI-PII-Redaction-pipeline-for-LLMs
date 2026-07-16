import re
from fastapi import FastAPI
from pydantic import BaseModel

# Mock clinical data simulating unredacted text
mock_clinical_note = """
Patient presented to the ER on 10/24/2023 complaining of severe chest pain.
Contact patient's primary care physician at john.smith@medical-clinic.com.
Emergency contact number: 555-867-5309. 
Patient history indicates previous surgery on 01/15/2019.
"""

def apply_regex_baseline(text: str) -> str:
    """Scans text for strict structural patterns and replaces them."""
    safe_text = text
    
    # Redact Emails
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    safe_text = re.sub(email_pattern, '<EMAIL_REDACTED>', safe_text)
    
    # Redact Phone Numbers
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    safe_text = re.sub(phone_pattern, '<PHONE_REDACTED>', safe_text)
    
    # Redact Dates (MM/DD/YYYY)
    date_pattern = r'\b\d{2}/\d{2}/\d{4}\b'
    safe_text = re.sub(date_pattern, '<DATE_REDACTED>', safe_text)
    
    return safe_text

# Initialize FastAPI
app = FastAPI(title="PHI Redaction Proxy", version="1.0")

class ProxyRequest(BaseModel):
    prompt: str

@app.post("/v1/intercept")
async def intercept_and_redact(request: ProxyRequest):
    raw_text = request.prompt
    redacted_text = apply_regex_baseline(raw_text)
    return {
        "status": "success",
        "original_length": len(raw_text),
        "safe_prompt": redacted_text
    }