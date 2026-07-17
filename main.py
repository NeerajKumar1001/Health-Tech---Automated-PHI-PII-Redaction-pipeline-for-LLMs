import re
from fastapi import FastAPI
from pydantic import BaseModel
# Import our new data loader module!
from dataset_loader import get_random_clinical_note

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

app = FastAPI(title="PHI Redaction Proxy", version="1.1")

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

# --- NEW ENDPOINT FOR DAY 2 ---
@app.get("/v1/mock-note")
async def fetch_mock_note():
    """Returns a random, unredacted clinical note from our database."""
    note = get_random_clinical_note()
    return {"status": "success", "data": note}