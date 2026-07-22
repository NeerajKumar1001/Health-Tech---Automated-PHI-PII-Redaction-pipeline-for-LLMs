from presidio_analyzer import AnalyzerEngine

# Initialize the NLP model
analyzer = AnalyzerEngine()

def apply_nlp_redaction(text: str):
    """
    Scans text for contextual PHI, replaces it with unique tags, 
    and generates a secure mapping dictionary for two-way reversal.
    """
    results = analyzer.analyze(text=text, language='en')
    
    # Sort from end to beginning to prevent string index errors during replacement
    results = sorted(results, key=lambda x: x.start, reverse=True)
    
    secure_mapping = {}
    safe_text = text
    entity_counters = {}
    
    for res in results:
        entity_type = res.entity_type
        
        # Track counts (e.g., PERSON_1, PERSON_2)
        if entity_type not in entity_counters:
            entity_counters[entity_type] = 1
        else:
            entity_counters[entity_type] += 1
            
        placeholder = f"<{entity_type}_{entity_counters[entity_type]}>"
        original_value = text[res.start:res.end]
        
        # Save to dictionary and replace in text
        secure_mapping[placeholder] = original_value
        safe_text = safe_text[:res.start] + placeholder + safe_text[res.end:]
        
    return safe_text, secure_mapping