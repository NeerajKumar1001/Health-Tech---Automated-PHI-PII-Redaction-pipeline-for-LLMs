import re
from presidio_analyzer import AnalyzerEngine
from custom_recognizers import get_mrn_recognizer, get_facility_unit_recognizer

# Known medical eponyms to preserve
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

CLINICAL_CONDITION_SUFFIXES = [
    "disease", "syndrome", "lymphoma", "palsy", 
    "chorea", "dementia", "disorder", "phenomenon"
]

# 1. Initialize Analyzer and Register Custom Recognizers
analyzer = AnalyzerEngine()
analyzer.registry.add_recognizer(get_mrn_recognizer())
analyzer.registry.add_recognizer(get_facility_unit_recognizer())

def apply_nlp_redaction(text: str):
    """
    Scans text for general PHI, custom medical entities (MRN, Ward/Facility),
    while protecting medical eponyms from accidental redaction.
    """
    # 2. Include custom entities in the analysis request
    target_entities = [
        "PERSON", "LOCATION", "ORGANIZATION", 
        "MEDICAL_RECORD_NUMBER", "HOSPITAL_FACILITY"
    ]
    
    results = analyzer.analyze(
        text=text, 
        entities=target_entities, 
        language='en',
        allow_list=MEDICAL_EPONYM_ALLOWLIST
    )
    
    # Contextual check to preserve medical conditions
    filtered_results = []
    for res in results:
        if res.entity_type == "PERSON":
            trailing_text = text[res.end:].strip().lower()
            is_medical_condition = any(
                trailing_text.startswith(suffix) for suffix in CLINICAL_CONDITION_SUFFIXES
            )
            if is_medical_condition:
                continue
                
        filtered_results.append(res)
    
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