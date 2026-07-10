from models.screen import ValidationRule, RestMetadata, ComponentDef, ButtonDef, ScreenDef
from models.request import StartRequest, NextStepRequest, NextStepResponse
from pydantic import ValidationError
import pytest

def test_validation_rule():
    rule = ValidationRule(type="required", message="Field is required")
    assert rule.type == "required"
    assert rule.message == "Field is required"

    with pytest.raises(ValidationError):
        ValidationRule(type="invalid_type")

def test_rest_metadata():
    metadata = RestMetadata(endpoint="/api/data", method="GET")
    assert metadata.endpoint == "/api/data"
    assert metadata.method == "GET"

    with pytest.raises(ValidationError):
        RestMetadata(endpoint="/api/data", method="PUT")

def test_component_def():
    comp = ComponentDef(id="comp1", type="text", label="Enter text")
    assert comp.id == "comp1"
    assert comp.type == "text"
    assert comp.label == "Enter text"

    with pytest.raises(ValidationError):
        ComponentDef(id="comp2", type="invalid_type", label="Invalid")

def test_button_def():
    btn = ButtonDef(id="btn1", label="Next", action="next_step")
    assert btn.id == "btn1"
    assert btn.action == "next_step"

    with pytest.raises(ValidationError):
        ButtonDef(id="btn2", label="Invalid", action="invalid_action")

def test_screen_def():
    screen = ScreenDef(
        id="screen1",
        header="Header",
        content="Content",
        components=[ComponentDef(id="comp1", type="text", label="Label")],
        buttons=[ButtonDef(id="btn1", label="Next", action="next_step")]
    )
    assert screen.id == "screen1"
    assert len(screen.components) == 1
    assert len(screen.buttons) == 1

def test_start_request():
    req = StartRequest(service_id="service1")
    assert req.service_id == "service1"

def test_next_step_request():
    req = NextStepRequest(service_id="service1", current_screen_id="screen1", answers={"comp1": "value1"})
    assert req.service_id == "service1"
    assert req.current_screen_id == "screen1"
    assert req.answers["comp1"] == "value1"

def test_next_step_response():
    resp = NextStepResponse(completed=True)
    assert resp.completed is True
    assert resp.next_screen is None

    screen = ScreenDef(
        id="screen1",
        header="Header",
        content="Content",
        components=[],
        buttons=[]
    )
    resp2 = NextStepResponse(next_screen=screen)
    assert resp2.next_screen is not None
    assert resp2.next_screen.id == "screen1"
    assert resp2.completed is False
