from fastapi.testclient import TestClient

from CTFe.main import app


def test_create_player():
    client = TestClient(app)
    
    json_data = {
        "username": "player1",
        "password": "secret",
    }

    response = client.post("/player", json=json_data)

    assert response.status_code == 401
    assert response.json() == {"detail": "You are not logged in"}
