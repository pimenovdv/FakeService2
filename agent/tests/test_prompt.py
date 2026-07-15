import unittest
import json
from src.prompt import generate_system_prompt

class TestPromptEngineering(unittest.TestCase):
    def test_generate_system_prompt(self):
        parsed_screen = {
            "fields": [
                {
                    "tag": "input",
                    "id": "name",
                    "name": "user_name",
                    "type": "text",
                    "label": "Name",
                    "attributes": {
                        "required": True
                    }
                }
            ],
            "buttons": [
                {
                    "text": "Submit",
                    "type": "submit"
                }
            ]
        }

        prompt = generate_system_prompt(parsed_screen)

        # Check that prompt contains required instructions
        self.assertIn("You are an agent helping a user fill out a form.", prompt)
        self.assertIn("Ask the user for this information, use autocomplete features when available, and determine the values to input.", prompt)

        # Check that prompt contains the JSON representation of fields
        expected_json = json.dumps(parsed_screen, ensure_ascii=False, indent=2)
        self.assertIn(expected_json, prompt)

    def test_generate_system_prompt_with_config(self):
        parsed_screen = {"fields": []}

        # Test custom prompt
        prompt = generate_system_prompt(
            parsed_screen,
            service_id="custom_service",
            config_path="tests/test_config.json"
        )
        self.assertIn("You are a specialized agent for the custom service.", prompt)

    def test_generate_system_prompt_with_config_fallback(self):
        parsed_screen = {"fields": []}

        # Test fallback when service not in config
        prompt = generate_system_prompt(
            parsed_screen,
            service_id="unknown_service",
            config_path="tests/test_config.json"
        )
        self.assertIn("You are an agent helping a user fill out a form.", prompt)
