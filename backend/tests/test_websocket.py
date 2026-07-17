from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_websocket_endpoint():
    with client.websocket_connect("/api/ws/notifications") as websocket:
        websocket.send_text("Hello World")
        data = websocket.receive_text()
        assert data == "Echo: Hello World"

        websocket.send_text("Another Message")
        data = websocket.receive_text()
        assert data == "Echo: Another Message"
