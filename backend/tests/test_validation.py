from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_next_step_validation_error():
    response = client.post("/api/screens/next_step", json={
        "service_id": "service_1",
        "current_screen_id": "screen_1",
        "answers": {}
    })
    assert response.status_code == 400
    assert response.json() == {"detail": "Name is required"}


def test_regex_validation():
    response = client.post("/api/screens/next_step", json={
        "service_id": "service_validation",
        "current_screen_id": "screen_1",
        "answers": {"username": "Invalid User!"}
    })
    assert response.status_code == 400
    assert response.json() == {"detail": "Username must be alphanumeric and lowercase"}


def test_min_value_validation():
    response = client.post("/api/screens/next_step", json={
        "service_id": "service_validation",
        "current_screen_id": "screen_1",
        "answers": {"age": "17"}
    })
    assert response.status_code == 400
    assert response.json() == {"detail": "Must be at least 18"}


def test_max_value_validation():
    response = client.post("/api/screens/next_step", json={
        "service_id": "service_validation",
        "current_screen_id": "screen_1",
        "answers": {"age": "100"}
    })
    assert response.status_code == 400
    assert response.json() == {"detail": "Must be at most 99"}


def test_min_length_validation():
    response = client.post("/api/screens/next_step", json={
        "service_id": "service_validation",
        "current_screen_id": "screen_1",
        "answers": {"bio": "short"}
    })
    assert response.status_code == 400
    assert response.json() == {"detail": "Bio too short"}


def test_max_length_validation():
    response = client.post("/api/screens/next_step", json={
        "service_id": "service_validation",
        "current_screen_id": "screen_1",
        "answers": {"bio": "a" * 51}
    })
    assert response.status_code == 400
    assert response.json() == {"detail": "Bio too long"}


def test_cross_field_match_failure():
    response = client.post("/api/screens/next_step", json={
        "service_id": "service_validation",
        "current_screen_id": "screen_1",
        "answers": {
            "password": "mypassword",
            "confirm_password": "differentpassword"
        }
    })
    assert response.status_code == 400
    assert response.json() == {"detail": "Passwords do not match"}


def test_cross_field_required_if_failure():
    response = client.post("/api/screens/next_step", json={
        "service_id": "service_validation",
        "current_screen_id": "screen_1",
        "answers": {
            "password": "mypassword",
            "confirm_password": "mypassword",
            "has_pet": "yes"
            # pet_name is missing
        }
    })
    assert response.status_code == 400
    assert response.json() == {"detail": "Pet name is required if you have a pet"}


def test_all_validations_pass():
    response = client.post("/api/screens/next_step", json={
        "service_id": "service_validation",
        "current_screen_id": "screen_1",
        "answers": {
            "username": "validuser123",
            "age": "25",
            "bio": "this is a valid bio",
            "password": "mypassword",
            "confirm_password": "mypassword",
            "has_pet": "no"
        }
    })
    assert response.status_code == 200
    assert response.json() == {"completed": True, "next_screen": None}
