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

def test_parse_malformed_html_graceful_fallback(monkeypatch):
    html = '<input type="text" id="bad">'
    parser = ScreenParser(html)

    # Mock soup.find_all to raise an exception simulating a catastrophic parsing failure
    def mock_find_all(*args, **kwargs):
        raise Exception("Parsing died")

    monkeypatch.setattr(parser.soup, 'find_all', mock_find_all)

    result = parser.parse()

    assert result == {"fields": [], "buttons": [], "error": "Failed to parse HTML"}
