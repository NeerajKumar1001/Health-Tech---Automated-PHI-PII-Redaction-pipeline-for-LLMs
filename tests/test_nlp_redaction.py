import pytest
from nlp_engine import apply_nlp_redaction

class TestMedicalEponyms:
    """Verifies that clinical conditions named after people are preserved."""
    
    def test_parkinsons_disease_preserved(self):
        text = "Patient was diagnosed with Parkinson's disease three years ago."
        safe_text, _ = apply_nlp_redaction(text)
        assert "Parkinson's disease" in safe_text
        assert "<PERSON" not in safe_text

    def test_crohns_disease_preserved(self):
        text = "The patient shows active Crohn's disease symptoms."
        safe_text, _ = apply_nlp_redaction(text)
        assert "Crohn's disease" in safe_text
        assert "<PERSON" not in safe_text

    def test_eponym_and_patient_in_same_sentence(self):
        text = "Patient Robert Parkinson was evaluated for Parkinson's disease."
        safe_text, mapping = apply_nlp_redaction(text)
        
        # Patient name should be redacted
        assert "Robert Parkinson" not in safe_text
        assert "<PERSON_1>" in safe_text
        
        # Medical condition should remain intact
        assert "Parkinson's disease" in safe_text


class TestCustomRecognizers:
    """Verifies custom recognizers for MRNs and Hospital Facilities."""
    
    def test_mrn_redaction(self):
        text = "Patient record MRN-938475 was updated today."
        safe_text, mapping = apply_nlp_redaction(text)
        assert "MRN-938475" not in safe_text
        assert "<MEDICAL_RECORD_NUMBER_1>" in safe_text

    def test_hospital_facility_redaction(self):
        text = "Transfer the patient to Ward 4B immediately."
        safe_text, mapping = apply_nlp_redaction(text)
        assert "Ward 4B" not in safe_text
        assert "<HOSPITAL_FACILITY_1>" in safe_text


class TestContextualConfidence:
    """Verifies that thresholding prevents over-redaction of standard prose."""
    
    def test_clinical_prose_preservation(self):
        text = "The patient experienced mild headache and acute chest tightness."
        safe_text, mapping = apply_nlp_redaction(text)
        assert safe_text == text
        assert len(mapping) == 0