from CTFe.models import User
from . import (
    client,
    dal,
)


def test_login_player__missing_user_input():
    json_datas = [
        # Failed because no username or password fields
        {},
        # Failed because no password field
        {
            "username": "foo",
        },
        # Failed because no username field
        {
            "password": "foo",
        },
    ]

    for json_data in json_datas:
        response = client.post("/login", json=json_data)
        assert response.status_code == 422


def test_login_player__not_found():
    # Failed because user not found
    json_data = {
        "username": "foo",
        "password": "bar",
    }

    response = client.post("/login", json=json_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_login_player__found():
    # User exists
    json_data = {
        "username": "client1",
        "password": "secret",
    }

    response = client.post("/login", json=json_data)
    assert response.status_code == 200
    assert response.json() == {"id": 1, "username": json_data["username"]}
    assert "token" in response.cookies.keys()
