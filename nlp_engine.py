import re
from presidio_analyzer import AnalyzerEngine

# 1. Known medical eponyms that general NLP models frequently misclassify as PERSON
MEDICAL_EPONYM_ALLOWLIST = [
    "Parkinson's", "Parkinson", 
    "Alzheimer's", "Alzheimer", 
    "Crohn's", "Crohn", 
    "Hodgkin's", "Hodgkin", 
    "Bell's", 
    "Huntington's", "Huntington",
    "Raynaud's", "Raynaud",
    "Graves'", "Grave's"
]

# Clinical suffixes indicating a condition rather than an individual
CLINICAL_CONDITION_SUFFIXES = [
    "disease", "syndrome", "lymphoma", "palsy", 
    "chorea", "dementia", "disorder", "phenomenon"
]

# Initialize Presidio Analyzer
analyzer = AnalyzerEngine()

def apply_nlp_redaction(text: str):
    """
    Scans text for contextual PHI while protecting medical conditions 
    named after people (eponyms) from accidental redaction.
    """
    # Analyze text with Presidio while passing our allowlist
    results = analyzer.analyze(
        text=text, 
        entities=["PERSON", "LOCATION", "ORGANIZATION"], 
        language='en',
        allow_list=MEDICAL_EPONYM_ALLOWLIST
    )
    
    # Contextual check: Filter out any entity falsely flagged as PERSON 
    # if it is directly followed by a medical suffix (e.g., "Parkinson disease")
    filtered_results = []
    for res in results:
        if res.entity_type == "PERSON":
            # Extract text following the detected entity
            trailing_text = text[res.end:].strip().lower()
            
            # Check if the next word is a clinical condition indicator
            is_medical_condition = any(
                trailing_text.startswith(suffix) for suffix in CLINICAL_CONDITION_SUFFIXES
            )
            
            if is_medical_condition:
                continue  # Skip redacting this entity; it's a condition!
                
        filtered_results.append(res)
    
    # Sort results from end to start to maintain correct string indexing
    filtered_results = sorted(filtered_results, key=lambda x: x.start, reverse=True)
    
    secure_mapping = {}
    safe_text = text
    entity_counters = {}
    
    for res in filtered_results:
        entity_type = res.entity_type
        
        if entity_type not in entity_counters:
            entity_counters[entity_type] = 1
        else:
            entity_counters[entity_type] += 1
            
        placeholder = f"<{entity_type}_{entity_counters[entity_type]}>"
        original_value = text[res.start:res.end]
        
        secure_mapping[placeholder] = original_value
        safe_text = safe_text[:res.start] + placeholder + safe_text[res.end:]
        
    return safe_text, secure_mapping