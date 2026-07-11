from bs4 import BeautifulSoup
from typing import Dict, Any, List

class ScreenParser:
    """
    Parses a pre-rendered HTML screen and extracts form fields, labels, buttons,
    and validation requirements.
    """

    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, 'html.parser')

    def parse(self) -> Dict[str, Any]:
        """
        Extracts structural requirements of the screen.
        """
        result = {
            "fields": [],
            "buttons": []
        }

        # Extract all input-like elements
        for element in self.soup.find_all(['input', 'select', 'textarea']):
            field_info = self._parse_field(element)
            if field_info:
                result["fields"].append(field_info)

        # Extract buttons
        for button in self.soup.find_all('button'):
            btn_info = {
                "text": button.get_text(strip=True),
                "type": button.get('type', 'button'),
                "id": button.get('id'),
                "name": button.get('name')
            }
            # Clean up Nones
            btn_info = {k: v for k, v in btn_info.items() if v is not None}
            result["buttons"].append(btn_info)

        return result

    def _parse_field(self, element) -> Dict[str, Any]:
        tag_name = element.name
        field_id = element.get('id')
        name = element.get('name')

        # We need an id or name to identify the field, though id is preferred for labels
        if not field_id and not name:
            return {}

        field_info = {
            "tag": tag_name,
            "id": field_id,
            "name": name,
            "type": element.get('type') if tag_name == 'input' else None,
            "label": self._find_label(field_id),
            "attributes": self._extract_attributes(element)
        }

        # Clean up Nones
        field_info = {k: v for k, v in field_info.items() if v is not None}

        # Extract options for select elements
        if tag_name == 'select':
            options = []
            for opt in element.find_all('option'):
                options.append({
                    "value": opt.get('value'),
                    "text": opt.get_text(strip=True)
                })
            field_info["options"] = options

        return field_info

    def _find_label(self, field_id: str) -> str | None:
        if not field_id:
            return None
        label = self.soup.find('label', attrs={'for': field_id})
        if label:
            return label.get_text(strip=True)
        return None

    def _extract_attributes(self, element) -> Dict[str, Any]:
        attrs = {}
        # List of validation and structural attributes to look for
        target_attrs = ['required', 'minlength', 'maxlength', 'pattern', 'placeholder', 'value', 'min', 'max', 'step']

        for attr in target_attrs:
            if element.has_attr(attr):
                val = element.get(attr)
                # Handle boolean attributes like 'required' which might have no value or equal to their name
                if attr == 'required' and (val == '' or val == 'required' or val is None):
                    attrs[attr] = True
                else:
                    attrs[attr] = val

        return attrs
