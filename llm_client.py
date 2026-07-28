import asyncio

async def query_external_llm(safe_prompt: str) -> str:
    """
    Simulates sending the sanitized prompt to an external LLM provider.
    """
    await asyncio.sleep(0.2)
    return (
        f"Summary of clinical note: Patient <PERSON_1> was evaluated. "
        f"The attending physician recommends continued monitoring in <HOSPITAL_FACILITY_1>. "
        f"Please reference MRN: <MEDICAL_RECORD_NUMBER_1> for updates."
    )

# Alias to support both naming styles
forward_to_external_llm = query_external_llm