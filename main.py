import re
from fastapi import FastAPI
from pydantic import BaseModel
from dataset_loader import get_random_clinical_note
from audit_logger import log_transaction
from nlp_engine import apply_nlp_redaction
from llm_client import query_external_llm
from reversal_engine import reconstruct_phi_in_response

def apply_regex_baseline(text: str) -> str:
    safe_text = text
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    safe_text = re.sub(email_pattern, '<EMAIL_REDACTED>', safe_text)
    phone_pattern = r'\b(?:\d{3}[-.\s]?)?\d{3}[-.]\d{4}\b'
    safe_text = re.sub(phone_pattern, '<PHONE_REDACTED>', safe_text)
    date_pattern = r'\b(?:\d{1,4}[-/]\d{1,2}[-/]\d{1,4})\b'
    safe_text = re.sub(date_pattern, '<DATE_REDACTED>', safe_text)
    return safe_text

app = FastAPI(title="PHI Redaction & LLM Secure Proxy", version="3.0")

class ProxyRequest(BaseModel):
    prompt: str

@app.post("/v1/intercept")
async def intercept_and_redact(request: ProxyRequest):
    raw_text = request.prompt
    regex_safe_text = apply_regex_baseline(raw_text)
    final_safe_text, reversal_map = apply_nlp_redaction(regex_safe_text)
    
    txn_id = log_transaction(
        endpoint="/v1/intercept",
        original_length=len(raw_text),
        safe_length=len(final_safe_text)
    )
    
    return {
        "status": "success",
        "transaction_id": txn_id,
        "original_length": len(raw_text),
        "safe_prompt": final_safe_text,
        "secure_mapping": reversal_map
    }

@app.post("/v1/chat/completions")
async def secure_llm_chat(request: ProxyRequest):
    """
    End-to-End Secure Flow:
    1. Intercept raw prompt containing PHI.
    2. Anonymize PHI via Regex + NLP Engine.
    3. Forward sanitized prompt to LLM.
    4. Intercept LLM response and reverse PHI tags back to original text.
    5. Return unredacted, personalized response to client securely.
    """
    raw_prompt = request.prompt
    
    # 1. Redact
    regex_safe = apply_regex_baseline(raw_prompt)
    sanitized_prompt, reversal_map = apply_nlp_redaction(regex_safe)
    
    # 2. Forward to LLM (External server only sees sanitized_prompt)
    llm_raw_response = await query_external_llm(sanitized_prompt)
    
    # 3. Un-redact / Reconstruct PHI locally
    final_user_response = reconstruct_phi_in_response(llm_raw_response, reversal_map)
    
    txn_id = log_transaction(
        endpoint="/v1/chat/completions",
        original_length=len(raw_prompt),
        safe_length=len(sanitized_prompt)
    )
    
    return {
        "status": "success",
        "transaction_id": txn_id,
        "sanitized_prompt_sent_to_llm": sanitized_prompt,
        "llm_raw_response": llm_raw_response,
        "final_reconstructed_response": final_user_response
    }

@app.get("/v1/mock-note")
async def fetch_mock_note():
    note = get_random_clinical_note()
    return {"status": "success", "data": note}