import logging
from bs4 import BeautifulSoup
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

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
        logger.debug("ScreenParser parsing HTML")
        try:
            result = {
                "fields": [],
                "buttons": [],
                "dialogs": [],
                "scripts": [],
                "crossValidations": []
            }

            # Extract cross validations
            cv_script = self.soup.find('div', id='cross-validations-data')
            if cv_script and cv_script.string:
                try:
                    import json
                    result["crossValidations"] = json.loads(cv_script.string.strip())
                except Exception as e:
                    logger.error(f"Failed to parse cross validations: {e}")
                cv_script.extract()

            # Extract scripts
            for script in self.soup.find_all('script'):
                script_info = {}
                if script.has_attr('src'):
                    script_info['src'] = script.get('src')
                if script.string:
                    script_info['content'] = script.string.strip()

                # Only append if we found something useful
                if script_info:
                    result["scripts"].append(script_info)
                script.extract() # Remove script so it's processed

            # Extract dialogs first so their children don't pollute the main fields
            for dialog in self.soup.find_all('dialog'):
                dialog_info = {
                    "id": dialog.get('id'),
                    "fields": [],
                    "buttons": []
                }
                for element in dialog.find_all(['input', 'select', 'textarea']):
                    field_info = self._parse_field(element)
                    if field_info:
                        dialog_info["fields"].append(field_info)
                for button in dialog.find_all('button'):
                    btn_info = self._parse_button(button)
                    if btn_info:
                        dialog_info["buttons"].append(btn_info)

                # Clean up Nones in dialog_info
                dialog_info = {k: v for k, v in dialog_info.items() if v is not None}
                result["dialogs"].append(dialog_info)
                dialog.extract() # Remove the dialog from soup so it's not processed again

            # Extract all input-like elements from main body
            for element in self.soup.find_all(['input', 'select', 'textarea']):
                field_info = self._parse_field(element)
                if field_info:
                    result["fields"].append(field_info)

            # Extract buttons from main body
            for button in self.soup.find_all('button'):
                btn_info = self._parse_button(button)
                if btn_info:
                    result["buttons"].append(btn_info)

            logger.info(f"ScreenParser extracted {len(result['fields'])} fields, {len(result['buttons'])} buttons, and {len(result.get('dialogs', []))} dialogs")
            return result
        except Exception as e:
            logger.error(f"ScreenParser failed to parse HTML: {e}")
            return {"fields": [], "buttons": [], "error": "Failed to parse HTML"}

    def _parse_button(self, button) -> Dict[str, Any]:
        btn_info = {
            "text": button.get_text(strip=True),
            "type": button.get('type', 'button'),
            "id": button.get('id'),
            "name": button.get('name')
        }

        # Extract inline event handlers (attributes starting with 'on')
        events = {}
        for attr, val in button.attrs.items():
            if attr.startswith('on'):
                events[attr] = val
        if events:
            btn_info['events'] = events

        # Clean up Nones
        return {k: v for k, v in btn_info.items() if v is not None}

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
        target_attrs = ['required', 'minlength', 'maxlength', 'pattern', 'placeholder', 'value', 'min', 'max', 'step', 'accept', 'multiple']

        for attr in target_attrs:
            if element.has_attr(attr):
                val = element.get(attr)
                # Handle boolean attributes like 'required' which might have no value or equal to their name
                if attr == 'required' and (val == '' or val == 'required' or val is None):
                    attrs[attr] = True
                else:
                    attrs[attr] = val

        # Extract inline event handlers (attributes starting with 'on')
        for attr, val in element.attrs.items():
            if attr.startswith('on'):
                attrs[attr] = val

        return attrs
