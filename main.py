import re
from fastapi import FastAPI
from pydantic import BaseModel
from dataset_loader import get_random_clinical_note
from audit_logger import log_transaction

# Import our new NLP engine
from nlp_engine import apply_nlp_redaction

def apply_regex_baseline(text: str) -> str:
    safe_text = text
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    safe_text = re.sub(email_pattern, '<EMAIL_REDACTED>', safe_text)
    phone_pattern = r'\b(?:\d{3}[-.\s]?)?\d{3}[-.]\d{4}\b'
    safe_text = re.sub(phone_pattern, '<PHONE_REDACTED>', safe_text)
    date_pattern = r'\b(?:\d{1,4}[-/]\d{1,2}[-/]\d{1,4})\b'
    safe_text = re.sub(date_pattern, '<DATE_REDACTED>', safe_text)
    return safe_text

app = FastAPI(title="PHI Redaction Proxy", version="1.4")

class ProxyRequest(BaseModel):
    prompt: str

@app.post("/v1/intercept")
async def intercept_and_redact(request: ProxyRequest):
    raw_text = request.prompt
    
    # LAYER 1: Fast Regex filtering
    regex_safe_text = apply_regex_baseline(raw_text)
    
    # LAYER 2: Contextual NLP filtering
    final_safe_text = apply_nlp_redaction(regex_safe_text)
    
    txn_id = log_transaction(
        endpoint="/v1/intercept",
        original_length=len(raw_text),
        safe_length=len(final_safe_text)
    )
    
    return {
        "status": "success",
        "transaction_id": txn_id,
        "original_length": len(raw_text),
        "safe_prompt": final_safe_text
    }

@app.get("/v1/mock-note")
async def fetch_mock_note():
    note = get_random_clinical_note()
    return {"status": "success", "data": note}