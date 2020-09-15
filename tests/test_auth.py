from datetime import (
    datetime,
    timedelta,
)

from CTFe.models import User
from CTFe.config import constants
from CTFe.utils import jwt_utils

from . import (
    client,
    dal,
)


def test_login__missing_user_input():
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


def test_login__user_not_found():
    # Failed because user not found
    json_data = {
        "username": "foo",
        "password": "bar",
    }

    response = client.post("/login", json=json_data)

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_login__user_found():
    # User exists
    json_data = {
        "username": "client1",
        "password": "secret",
    }

    response = client.post("/login", json=json_data)

    assert response.status_code == 200
    assert response.json() == {"id": 1, "username": json_data["username"]}
    assert "token" in response.cookies.keys()


def test_logout__token_not_found():
    """ Remove token on purpose """
    token = client.cookies["token"]
    del client.cookies["token"]

    response = client.post("/logout")

    assert response.status_code == 401
    assert response.json() == {"detail": "You are not logged in"}
    assert "token" not in response.cookies.keys()

    client.cookies["token"] = token


def test_logout__token_expired():
    """ Expire token on purpose """
    old_token = client.cookies["token"]
    exp = (datetime.now() -
           timedelta(minutes=constants.JWT_EXPIRE_TIME)).timestamp()

    payload = jwt_utils.decode(old_token)
    payload.update({"exp": exp})

    new_token = jwt_utils.encode(payload)
    client.cookies["token"] = new_token

    response = client.post("/logout")

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}

    client.cookies["token"] = old_token


def test_logout__invalid_token():
    """ No records in redis """
    old_token = client.cookies["token"]

    payload = jwt_utils.decode(old_token)
    payload.update({"sub": "-1"})

    new_token = jwt_utils.encode(payload)
    client.cookies["token"] = new_token

    response = client.post("/logout")

    assert response.status_code == 401
    assert response.json() == {"detail": "Can not retrieve user"}

    client.cookies["token"] = old_token


def test_logout__success():
    response = client.post("/logout")

    assert response.status_code == 204
