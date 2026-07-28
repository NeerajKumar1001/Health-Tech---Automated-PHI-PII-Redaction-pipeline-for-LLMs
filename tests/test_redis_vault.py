import pytest
from redis_vault import save_token_mapping, get_token_mapping, clear_session_vault
from reversal_engine import reverse_pseudonymization

def test_redis_token_vault_flow():
    session_id = "test-session-redis-101"
    mock_mapping = {
        "<PERSON_1>": "Dr. Adams",
        "<HOSPITAL_FACILITY_1>": "Ward 4B"
    }
    
    # Store in Redis Vault
    saved = save_token_mapping(session_id, mock_mapping)
    assert saved is True
    
    # Retrieve from Redis Vault
    retrieved = get_token_mapping(session_id)
    assert retrieved == mock_mapping
    
    # Test Pseudonymization Reversal
    llm_text = "Consultation with <PERSON_1> at <HOSPITAL_FACILITY_1>."
    reversed_text = reverse_pseudonymization(session_id, llm_text)
    
    assert "Dr. Adams" in reversed_text
    assert "Ward 4B" in reversed_text
    assert "<PERSON_1>" not in reversed_text
    
    # Cleanup session key
    clear_session_vault(session_id)