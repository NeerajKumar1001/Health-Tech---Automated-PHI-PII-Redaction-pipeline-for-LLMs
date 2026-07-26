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
    "PERSON": 0.50,
    "MEDICAL_RECORD_NUMBER": 0.50,
    "HOSPITAL_FACILITY": 0.60,
    "LOCATION": 0.70,
    "ORGANIZATION": 0.70
}

DEFAULT_GLOBAL_THRESHOLD = 0.60

# Initialize Analyzer and Register Custom Recognizers
analyzer = AnalyzerEngine()
analyzer.registry.add_recognizer(get_mrn_recognizer())
analyzer.registry.add_recognizer(get_facility_unit_recognizer())

# Domain priority mapping for tie-breaking overlapping entity spans
DOMAIN_ENTITY_PRIORITY = {
    "MEDICAL_RECORD_NUMBER": 2,
    "HOSPITAL_FACILITY": 2,
    "PERSON": 1,
    "LOCATION": 0,
    "ORGANIZATION": 0
}

def remove_overlapping_entities(results):
    """
    Deduplicates overlapping entities by keeping highest confidence score,
    domain priority, and longer text spans.
    """
    # Sort by Score (descending) -> Domain Priority (descending) -> Span Length (descending)
    sorted_candidates = sorted(
        results, 
        key=lambda x: (
            x.score, 
            DOMAIN_ENTITY_PRIORITY.get(x.entity_type, 0), 
            x.end - x.start
        ), 
        reverse=True
    )
    
    non_overlapping = []
    for cand in sorted_candidates:
        overlap = False
        for kept in non_overlapping:
            if max(cand.start, kept.start) < min(cand.end, kept.end):
                overlap = True
                break
        if not overlap:
            non_overlapping.append(cand)
            
    return non_overlapping

def apply_nlp_redaction(text: str, global_threshold: float = DEFAULT_GLOBAL_THRESHOLD):
    """
    Scans text for PHI using Presidio and filters results using entity-specific 
    confidence thresholds and overlapping entity deduplication.
    """
    target_entities = [
        "PERSON", "LOCATION", "ORGANIZATION", 
        "MEDICAL_RECORD_NUMBER", "HOSPITAL_FACILITY"
    ]
    
    raw_results = analyzer.analyze(
        text=text, 
        entities=target_entities, 
        language='en',
        score_threshold=0.30,
        allow_list=MEDICAL_EPONYM_ALLOWLIST
    )
    
    filtered_results = []
    for res in raw_results:
        min_required_score = ENTITY_SCORE_THRESHOLDS.get(res.entity_type, global_threshold)
        if res.score < min_required_score:
            continue
            
        if res.entity_type == "PERSON":
            trailing_text = text[res.end:].strip().lower()
            is_medical_condition = any(
                trailing_text.startswith(suffix) for suffix in CLINICAL_CONDITION_SUFFIXES
            )
            if is_medical_condition:
                continue
                
        filtered_results.append(res)
    
    # 1. Deduplicate overlapping entity spans
    filtered_results = remove_overlapping_entities(filtered_results)
    
    # 2. Sort from end to start for safe string replacement
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