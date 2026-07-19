import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_graphql_query_user():
    query = """
    query {
      user(id: 1) {
        id
        name
        email
      }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["user"]["id"] == 1
    assert data["data"]["user"]["name"] == "John Doe"
    assert data["data"]["user"]["email"] == "john@example.com"

def test_graphql_query_user_not_found():
    query = """
    query {
      user(id: 999) {
        id
        name
      }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["user"] is None
