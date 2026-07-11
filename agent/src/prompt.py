import json
from typing import Dict, Any

def generate_system_prompt(parsed_screen: Dict[str, Any]) -> str:
    """
    Generates a system prompt for the LLM based on the parsed screen requirements.
    """
    parsed_fields = json.dumps(parsed_screen, ensure_ascii=False, indent=2)

    prompt = (
        "You are an agent helping a user fill out a form. "
        f"The form requires the following fields:\n{parsed_fields}\n"
        "Ask the user for this information, use autocomplete features when available, "
        "and determine the values to input."
    )

    return prompt
