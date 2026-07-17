import json
import random

def load_mock_dataset(filepath: str = "mock_data.json"):
    """Reads the JSON file containing synthetic medical notes."""
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return [{"error": "Mock data file not found."}]

def get_random_clinical_note():
    """Fetches a random note from the dataset to test our proxy."""
    dataset = load_mock_dataset()
    return random.choice(dataset)