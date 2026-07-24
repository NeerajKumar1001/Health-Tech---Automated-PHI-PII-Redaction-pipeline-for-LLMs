from presidio_analyzer import PatternRecognizer, Pattern

def get_mrn_recognizer() -> PatternRecognizer:
    """
    Custom recognizer for Medical Record Numbers (MRNs).
    Matches patterns like MRN-123456, MRN: 987654, or MRN 456789.
    """
    mrn_pattern = Pattern(
        name="mrn_pattern",
        regex=r"\b(?:MRN|mrn)[:#\s-]*\d{6,8}\b",
        score=0.95
    )
    return PatternRecognizer(
        supported_entity="MEDICAL_RECORD_NUMBER",
        patterns=[mrn_pattern],
        context=["mrn", "patient", "record", "chart", "id"]
    )

def get_facility_unit_recognizer() -> PatternRecognizer:
    """
    Custom recognizer for specific hospital wards, wings, and units.
    Matches phrases like Ward 3B, ICU Wing, Cardiology Unit, Building 4.
    """
    facility_pattern = Pattern(
        name="facility_pattern",
        regex=r"\b(?:Ward|Wing|Unit|Building|Floor|Room)\s+[A-Z0-9-]+\b",
        score=0.85
    )
    return PatternRecognizer(
        supported_entity="HOSPITAL_FACILITY",
        patterns=[facility_pattern],
        context=["admitted", "transferred", "located", "clinic", "hospital", "dept"]
    )