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

# Entity-specific confidence thresholds
ENTITY_SCORE_THRESHOLDS = {
    "PERSON": 0.50,                   # Lower threshold for high-risk patient/doctor names
    "MEDICAL_RECORD_NUMBER": 0.50,   # Lower threshold for critical IDs
    "HOSPITAL_FACILITY": 0.60,       # Moderate threshold
    "LOCATION": 0.70,                # Higher threshold to avoid redacting clinical terms
    "ORGANIZATION": 0.70             # Higher threshold for general orgs
}

DEFAULT_GLOBAL_THRESHOLD = 0.60

# Initialize Analyzer and Register Custom Recognizers
analyzer = AnalyzerEngine()
analyzer.registry.add_recognizer(get_mrn_recognizer())
analyzer.registry.add_recognizer(get_facility_unit_recognizer())

def apply_nlp_redaction(text: str, global_threshold: float = DEFAULT_GLOBAL_THRESHOLD):
    """
    Scans text for PHI using Presidio and filters results using entity-specific 
    and global confidence score thresholds.
    """
    target_entities = [
        "PERSON", "LOCATION", "ORGANIZATION", 
        "MEDICAL_RECORD_NUMBER", "HOSPITAL_FACILITY"
    ]
    
    # Analyze text using global score threshold baseline
    raw_results = analyzer.analyze(
        text=text, 
        entities=target_entities, 
        language='en',
        score_threshold=0.30,  # Catch broad candidates first; we'll filter below
        allow_list=MEDICAL_EPONYM_ALLOWLIST
    )
    
    filtered_results = []
    for res in raw_results:
        # Check entity-specific score threshold
        min_required_score = ENTITY_SCORE_THRESHOLDS.get(res.entity_type, global_threshold)
        if res.score < min_required_score:
            continue  # Drop candidate if confidence score is too low
            
        # Contextual check to preserve medical eponyms/conditions
        if res.entity_type == "PERSON":
            trailing_text = text[res.end:].strip().lower()
            is_medical_condition = any(
                trailing_text.startswith(suffix) for suffix in CLINICAL_CONDITION_SUFFIXES
            )
            if is_medical_condition:
                continue
                
        filtered_results.append(res)
    
    # Sort results from end to start for string indexing safety
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