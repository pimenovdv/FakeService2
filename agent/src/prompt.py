import json
import os
from typing import Dict, Any, Optional

def generate_system_prompt(parsed_screen: Dict[str, Any], service_id: Optional[str] = None, config_path: Optional[str] = None) -> str:
    """
    Generates a system prompt for the LLM based on the parsed screen requirements.
    """
    parsed_fields = json.dumps(parsed_screen, ensure_ascii=False, indent=2)

    prompt_template = "You are an agent helping a user fill out a form."

    if config_path and service_id and os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                if service_id in config:
                    prompt_template = config[service_id]
        except Exception as e:
            pass # fallback to default

    prompt = (
        f"{prompt_template} "
        f"The form requires the following fields:\n{parsed_fields}\n"
        "Ask the user for this information, use autocomplete features when available, "
        "and determine the values to input. "
        "Analyze any extracted scripts and inline event handlers to simulate client-side behavior and evaluate simple state changes."
    )

    return prompt
