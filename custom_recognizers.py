from presidio_analyzer import PatternRecognizer, Pattern

def get_mrn_recognizer() -> PatternRecognizer:
    """
    Custom recognizer for Medical Record Numbers (MRNs).
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
    """
    facility_pattern = Pattern(
        name="facility_pattern",
        regex=r"\b(?:Ward|Wing|Unit|Building|Floor|Room)\s+[A-Z0-9-]+\b",
        score=0.95  # Increased score to 0.95 so domain-specific facilities beat generic LOCATION tags
    )
    return PatternRecognizer(
        supported_entity="HOSPITAL_FACILITY",
        patterns=[facility_pattern],
        context=["admitted", "transferred", "located", "clinic", "hospital", "dept"]
    )