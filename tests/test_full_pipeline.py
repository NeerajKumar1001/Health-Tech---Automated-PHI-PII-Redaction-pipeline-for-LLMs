import pytest
from reversal_engine import reconstruct_phi_in_response

def test_phi_reconstruction():
    llm_response = "Treatment plan for <PERSON_1> admitted to <HOSPITAL_FACILITY_1>."
    secure_mapping = {
        "<PERSON_1>": "Jane Doe",
        "<HOSPITAL_FACILITY_1>": "Ward 2A"
    }
    
    reconstructed = reconstruct_phi_in_response(llm_response, secure_mapping)
    
    assert "Jane Doe" in reconstructed
    assert "Ward 2A" in reconstructed
    assert "<PERSON_1>" not in reconstructed
    assert "<HOSPITAL_FACILITY_1>" not in reconstructed