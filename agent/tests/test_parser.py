import pytest
from src.parser import ScreenParser

def test_screen_parser_input():
    html = '''
    <label for="username">User Name</label>
    <input type="text" id="username" name="user" required minlength="3" placeholder="Enter name">
    '''
    parser = ScreenParser(html)
    result = parser.parse()

    assert len(result["fields"]) == 1
    field = result["fields"][0]
    assert field["tag"] == "input"
    assert field["id"] == "username"
    assert field["name"] == "user"
    assert field["type"] == "text"
    assert field["label"] == "User Name"
    assert field["attributes"]["required"] is True
    assert field["attributes"]["minlength"] == "3"
    assert field["attributes"]["placeholder"] == "Enter name"

def test_screen_parser_select():
    html = '''
    <label for="country">Country</label>
    <select id="country" name="country_id">
        <option value="1">US</option>
        <option value="2">UK</option>
    </select>
    '''
    parser = ScreenParser(html)
    result = parser.parse()

    assert len(result["fields"]) == 1
    field = result["fields"][0]
    assert field["tag"] == "select"
    assert field["id"] == "country"
    assert field["name"] == "country_id"
    assert field["label"] == "Country"

    options = field["options"]
    assert len(options) == 2
    assert options[0]["value"] == "1"
    assert options[0]["text"] == "US"
    assert options[1]["value"] == "2"
    assert options[1]["text"] == "UK"

def test_screen_parser_buttons():
    html = '''
    <button type="submit" id="submit-btn">Submit</button>
    <button type="button">Cancel</button>
    '''
    parser = ScreenParser(html)
    result = parser.parse()

    assert len(result["buttons"]) == 2
    assert result["buttons"][0]["type"] == "submit"
    assert result["buttons"][0]["id"] == "submit-btn"
    assert result["buttons"][0]["text"] == "Submit"

    assert result["buttons"][1]["type"] == "button"
    assert result["buttons"][1]["text"] == "Cancel"
    assert "id" not in result["buttons"][1]

def test_screen_parser_dialogs():
    html = '''
    <input type="text" id="main-input" name="main">
    <button type="submit">Main Submit</button>
    <dialog id="my-dialog">
        <label for="dialog-input">Dialog Input</label>
        <input type="text" id="dialog-input" name="d-input" required>
        <button type="button" id="dialog-btn">Dialog Action</button>
    </dialog>
    '''
    parser = ScreenParser(html)
    result = parser.parse()

    # Verify main elements
    assert len(result["fields"]) == 1
    assert result["fields"][0]["id"] == "main-input"
    assert len(result["buttons"]) == 1
    assert result["buttons"][0]["text"] == "Main Submit"

    # Verify dialog elements
    assert "dialogs" in result
    assert len(result["dialogs"]) == 1
    dialog = result["dialogs"][0]
    assert dialog["id"] == "my-dialog"

    assert len(dialog["fields"]) == 1
    assert dialog["fields"][0]["id"] == "dialog-input"
    assert dialog["fields"][0]["attributes"]["required"] is True

    assert len(dialog["buttons"]) == 1
    assert dialog["buttons"][0]["id"] == "dialog-btn"

def test_screen_parser_file_upload():
    html = '''
    <label for="file-upload">Upload File</label>
    <input type="file" id="file-upload" name="file" accept="image/*, .pdf" multiple>
    '''
    parser = ScreenParser(html)
    result = parser.parse()

    assert len(result["fields"]) == 1
    field = result["fields"][0]
    assert field["type"] == "file"
    assert field["attributes"]["accept"] == "image/*, .pdf"
    assert field["attributes"]["multiple"] == ""  # bs4 might return "" for boolean attributes with no value

def test_screen_parser_cross_validations():
    html = '''
    <div id="cross-validations-data">
    [
        {"type": "match", "fields": ["p1", "p2"], "message": "Passwords do not match"},
        {"type": "required_if", "condition_field": "has_pet", "condition_value": "yes", "target_field": "pet_name", "message": "Pet name required"}
    ]
    </div>
    '''
    parser = ScreenParser(html)
    result = parser.parse()

    assert "cross_validations" in result
    assert len(result["cross_validations"]) == 2
    assert result["cross_validations"][0]["type"] == "match"
    assert result["cross_validations"][0]["fields"] == ["p1", "p2"]
    assert result["cross_validations"][0]["message"] == "Passwords do not match"

    assert result["cross_validations"][1]["type"] == "required_if"
    assert result["cross_validations"][1]["condition_field"] == "has_pet"
    assert result["cross_validations"][1]["condition_value"] == "yes"
    assert result["cross_validations"][1]["target_field"] == "pet_name"
    assert result["cross_validations"][1]["message"] == "Pet name required"

def test_screen_parser_scripts():
    html = '''
    <script src="test.js"></script>
    <script>console.log("hello");</script>
    '''
    parser = ScreenParser(html)
    result = parser.parse()

    assert "scripts" in result
    assert len(result["scripts"]) == 2
    assert result["scripts"][0]["src"] == "test.js"
    assert result["scripts"][1]["content"] == 'console.log("hello");'

def test_screen_parser_inline_events():
    html = '''
    <input type="text" id="username" name="user" onchange="validateUser()">
    <button type="submit" id="submit-btn" onclick="submitForm()">Submit</button>
    '''
    parser = ScreenParser(html)
    result = parser.parse()

    assert len(result["fields"]) == 1
    field = result["fields"][0]
    assert "onchange" in field["attributes"]
    assert field["attributes"]["onchange"] == "validateUser()"

    assert len(result["buttons"]) == 1
    button = result["buttons"][0]
    assert "events" in button
    assert "onclick" in button["events"]
    assert button["events"]["onclick"] == "submitForm()"

def test_parse_malformed_html_graceful_fallback(monkeypatch):
    html = '<input type="text" id="bad">'
    parser = ScreenParser(html)

    # Mock soup.find_all to raise an exception simulating a catastrophic parsing failure
    def mock_find_all(*args, **kwargs):
        raise Exception("Parsing died")

    monkeypatch.setattr(parser.soup, 'find_all', mock_find_all)

    result = parser.parse()

    assert result == {"fields": [], "buttons": [], "error": "Failed to parse HTML"}

    def test_parse_cross_validations(self):
        html = '''
        <html>
            <body>
                <div id="cross-validations-data" style="display: none;">
                    [{"type": "match", "fields": ["p1", "p2"], "message": "Passwords do not match"}]
                </div>
                <input id="p1" type="text" />
                <input id="p2" type="text" />
            </body>
        </html>
        '''
        parser = ScreenParser(html)
        result = parser.parse()
        self.assertIn("crossValidations", result)
        self.assertEqual(len(result["crossValidations"]), 1)
        self.assertEqual(result["crossValidations"][0]["type"], "match")
        self.assertEqual(result["crossValidations"][0]["fields"], ["p1", "p2"])
