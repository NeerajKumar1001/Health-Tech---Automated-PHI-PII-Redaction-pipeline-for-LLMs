from redis_vault import get_token_mapping

def reverse_pseudonymization(session_id: str, llm_response: str) -> str:
    """
    Fetches mapping from Redis Vault using session_id and swaps 
    tokens back to original PHI values.
    """
    mapping = get_token_mapping(session_id)
    if not mapping:
        return llm_response

    return reconstruct_phi_in_response(llm_response, mapping)

def reconstruct_phi_in_response(llm_response: str, secure_mapping: dict) -> str:
    """
    Directly replaces placeholders in the LLM response with original values.
    """
    if not secure_mapping:
        return llm_response

    reconstructed_text = llm_response
    # Sort keys by length descending to prevent partial replacements
    sorted_tokens = sorted(secure_mapping.keys(), key=len, reverse=True)
    
    for token in sorted_tokens:
        original_value = secure_mapping[token]
        reconstructed_text = reconstructed_text.replace(token, original_value)
        
    return reconstructed_text