import re
from fastapi import FastAPI
from pydantic import BaseModel
# Import our new data loader module!
from dataset_loader import get_random_clinical_note

def apply_regex_baseline(text: str) -> str:
    """Scans text for strict structural patterns and replaces them."""
    safe_text = text
    
    # 1. Redact Emails (Unchanged - obfuscated emails will be handled by NLP later)
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    safe_text = re.sub(email_pattern, '<EMAIL_REDACTED>', safe_text)
    
    # 2. Redact Phone Numbers (Upgraded)
    # Added (?:\d{3}[-.\s]?)? to make the 3-digit area code optional.
    # It now catches both 10-digit (555-867-5309) and 7-digit local numbers (555-0198).
    phone_pattern = r'\b(?:\d{3}[-.\s]?)?\d{3}[-.]\d{4}\b'
    safe_text = re.sub(phone_pattern, '<PHONE_REDACTED>', safe_text)
    
    # 3. Redact Dates (Upgraded)
    # Changed \d{2} to \d{1,4} to allow 1 to 4 digits on either side of the slashes/dashes.
    # Catches: MM/DD/YYYY, M/D/YYYY, and YYYY-MM-DD (ISO).
    date_pattern = r'\b(?:\d{1,4}[-/]\d{1,2}[-/]\d{1,4})\b'
    safe_text = re.sub(date_pattern, '<DATE_REDACTED>', safe_text)
    
    return safe_text

app = FastAPI(title="PHI Redaction Proxy", version="1.2")

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