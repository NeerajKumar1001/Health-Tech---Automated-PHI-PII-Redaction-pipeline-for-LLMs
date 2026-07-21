from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# 1. Initialize the engines (This loads the English NLP model into memory)
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def apply_nlp_redaction(text: str) -> str:
    """
    Scans text for contextual PHI (Names, Locations, Organizations) 
    using Natural Language Processing and redacts them.
    """
    # 2. Analyze the text specifically for entities Regex can't catch
    results = analyzer.analyze(
        text=text, 
        entities=["PERSON", "LOCATION", "ORGANIZATION"], 
        language='en'
    )
    
    # 3. Anonymize the findings (replaces words with tags like <PERSON>)
    anonymized_result = anonymizer.anonymize(text=text, analyzer_results=results)
    
    return anonymized_result.text