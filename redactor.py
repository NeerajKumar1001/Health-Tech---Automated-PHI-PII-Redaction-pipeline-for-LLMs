from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine


analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()


def redact_text(text):

    results = analyzer.analyze(
        text=text,
        language="en"
    )

    anonymized = anonymizer.anonymize(
        text=text,
        analyzer_results=results
    )

    entities = []

    for result in results:
        entities.append(result.entity_type)

    return anonymized.text, entities