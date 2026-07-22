# HealthTech Automated PHI/PII Redaction Pipeline

A robust proxy service designed to intercept, redact, and securely log sensitive clinical data before it is transmitted to external LLM APIs. 

## Week 1 MVP Features
* **Hybrid Redaction Engine:** Combines Regex (for strict formats like dates/phones) with Microsoft Presidio NLP (for contextual entities like Names and Organizations).
* **Two-Way Pseudonymization:** Replaces PHI with traceable tags (`<PERSON_1>`) and generates a secure mapping dictionary for data reversal.
* **SOC-Compliant Audit Logging:** Generates local transaction logs tracking metadata and string lengths without ever writing raw PHI to disk.
* **Test-Driven Design:** Includes a Pytest suite highlighting known Regex gaps and verifying data integrity.
* **MIMIC-III Synthetic Data Loader:** Features a dedicated module for testing against realistic, unstructured clinical shorthand.

## Running the Proxy
1. Install dependencies: `pip install -r requirements.txt` (Ensure `en_core_web_lg` is downloaded for Spacy).
2. Start the server: `uvicorn main:app --reload`
3. Access the interactive dashboard at: `http://127.0.0.1:8000/docs`