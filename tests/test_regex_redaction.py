"""
Unit tests for the Day 1 regex-based PII redaction baseline in main.py.
Matches the actual apply_regex_baseline(text: str) -> str signature.

Run with: pytest tests/ -v
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import apply_regex_baseline


class TestEmailRedaction:
    def test_standard_email(self):
        text = "Contact patient at john.smith@email.com for follow-up."
        result = apply_regex_baseline(text)
        assert "john.smith@email.com" not in result

    def test_email_with_subdomain(self):
        text = "Reach the attending at dr.chen@cardiology.stmarys-hospital.org."
        result = apply_regex_baseline(text)
        assert "dr.chen@cardiology.stmarys-hospital.org" not in result

    def test_email_with_plus_tag(self):
        text = "Records sent to intake+urgent@clinic.net."
        result = apply_regex_baseline(text)
        assert "intake+urgent@clinic.net" not in result

    @pytest.mark.xfail(reason="Obfuscated/spelled-out emails need NLP, not regex - Week 2 hybrid engine")
    def test_obfuscated_email_known_gap(self):
        text = "Email him at john dot smith at hospital dot org."
        result = apply_regex_baseline(text)
        assert "john dot smith at hospital dot org" not in result


class TestPhoneRedaction:
    def test_standard_dashed_format(self):
        text = "Callback number: 555-123-4567."
        result = apply_regex_baseline(text)
        assert "555-123-4567" not in result

    def test_dotted_format(self):
        text = "Emergency contact: 555.123.4567"
        result = apply_regex_baseline(text)
        assert "555.123.4567" not in result

    def test_phone_with_extension(self):
        text = "Office line 555-123-4567 x204 for records requests."
        result = apply_regex_baseline(text)
        assert "555-123-4567" not in result

    @pytest.mark.xfail(reason="BUG found via mock_data.json MRN-938475: 7-digit local format "
                              "(no area code, e.g. 555-0198) does not match the 3-3-4 pattern. Fix Day 4.")
    def test_local_format_no_area_code_known_gap(self):
        text = "Patient phone: 555-0198."
        result = apply_regex_baseline(text)
        assert "555-0198" not in result

    @pytest.mark.xfail(reason="Parentheses format not handled by current regex - add Day 4")
    def test_parentheses_format_known_gap(self):
        text = "Patient reachable at (555) 123-4567 after 5pm."
        result = apply_regex_baseline(text)
        assert "(555) 123-4567" not in result

    @pytest.mark.xfail(reason="International formats not in Day 1 scope")
    def test_international_format_known_gap(self):
        text = "Patient traveling, reachable at +44 20 7946 0958."
        result = apply_regex_baseline(text)
        assert "+44 20 7946 0958" not in result


class TestDateRedaction:
    def test_slash_format(self):
        text = "DOB: 03/14/1985. Admitted on 07/01/2026."
        result = apply_regex_baseline(text)
        assert "03/14/1985" not in result
        assert "07/01/2026" not in result

    @pytest.mark.xfail(reason="ISO/dash date format (YYYY-MM-DD) not handled by current regex - Day 5")
    def test_dash_format_known_gap(self):
        text = "Procedure scheduled for 2026-07-20."
        result = apply_regex_baseline(text)
        assert "2026-07-20" not in result

    @pytest.mark.xfail(reason="Single-digit day/month not handled - pattern requires exactly 2 digits - Day 5")
    def test_single_digit_day_month_known_gap(self):
        text = "Follow-up visit: 7/1/2026."
        result = apply_regex_baseline(text)
        assert "7/1/2026" not in result

    @pytest.mark.xfail(reason="Month-name dates ('March 3, 2024') are Day 5 scope, not yet implemented")
    def test_month_name_date_known_gap(self):
        text = "Patient was diagnosed on March 3, 2024."
        result = apply_regex_baseline(text)
        assert "March 3, 2024" not in result


class TestClinicalContextPreserved:
    """Redaction must not eat clinical content it shouldn't touch."""

    def test_symptoms_survive_redaction(self):
        text = "Patient reports chest pain and shortness of breath. Contact: 555-123-4567."
        result = apply_regex_baseline(text)
        assert "chest pain" in result
        assert "shortness of breath" in result

    def test_diagnosis_survives_redaction(self):
        text = "Diagnosis: Type 2 diabetes mellitus. DOB: 03/14/1985."
        result = apply_regex_baseline(text)
        assert "Type 2 diabetes mellitus" in result