from datetime import (
    datetime,
    timedelta,
)

from fastapi.testclient import TestClient

from CTFe.main import app
from CTFe.models import User
from CTFe.schemas import user_schemas
from CTFe.config import constants
from CTFe.utils import (
    jwt_utils,
    redis_utils,
)
from . import (
    dal,
    redis_dal,
)


# /register Tests
# ----------------
def test_register__missing_user_input():
    client = TestClient(app)

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
        response = client.post("/register", json=json_data)

        assert response.status_code == 422


async def test_register__success():
    client = TestClient(app)

    json_data = {
        "username": "client1",
        "password": "secret",
    }

    response = client.post("/register", json=json_data)

    assert response.status_code == 200
    assert response.json() == {"id": 1, "username": json_data['username']}
    assert "token" in response.cookies.keys()

    token = response.cookies["token"]
    user_payload = await redis_utils.retrieve_payload(token, redis_dal)

    with dal.get_session_ctx() as session:
        db_user = session.query(User).get(user_payload.id)

        session.delete(db_user)
        session.commit()


def test_register__username_exists():
    client = TestClient(app)

    json_data = {
        "username": "client1",
        "password": "secret",
    }

    with dal.get_session_ctx() as session:
        db_user = User(
            username=json_data["username"], password=json_data["password"])

        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    response = client.post("/register", json=json_data)

    assert response.status_code == 409
    assert response.json() == {
        "detail": f"The username: { json_data['username'] } is already taken"}

    with dal.get_session_ctx() as session:
        session.delete(db_user)
        session.commit()


# /login Tests
# -------------
def test_login__missing_user_input():
    client = TestClient(app)

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
    client = TestClient(app)

    # Failed because user not found
    json_data = {
        "username": "foo",
        "password": "bar",
    }

    response = client.post("/login", json=json_data)

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_login__user_found():
    client = TestClient(app)

    # User exists
    json_data = {
        "username": "client1",
        "password": "secret",
    }

    with dal.get_session_ctx() as session:
        db_user = User(
            username=json_data["username"], password=json_data["password"])

        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    response = client.post("/login", json=json_data)

    assert response.status_code == 200
    assert "id" in response.json().keys()
    assert ("username", json_data["username"]) in response.json().items()
    assert "token" in response.cookies.keys()

    with dal.get_session_ctx() as session:
        session.delete(db_user)
        session.commit()


# /me Tests
# ----------
def test_logged_in_user_info__missing_token():
    client = TestClient(app)

    response = client.get("/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "You are not logged in"}


async def test_logged_in_user_info__expired_token():
    client = TestClient(app)

    with dal.get_session_ctx() as session:
        db_user = session.query(User).first()

    sub = str(db_user.id)
    iat = datetime.now().timestamp()
    exp = (datetime.now() - timedelta(minutes=15)).timestamp()

    token = jwt_utils.encode({
        "sub": sub,
        "iat": iat,
        "exp": exp,
    })

    client.cookies["token"] = token

    response = client.get("/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}

    await redis_utils.delete_key(user_payload.id, redis_dal)


def test_logged_in_user_info__invalid_token():
    client = TestClient(app)

    # No records in redis
    sub = "-1"
    iat = datetime.now().timestamp()
    exp = (datetime.now() + timedelta(minutes=15)).timestamp()

    token = jwt_utils.encode({
        "sub": sub,
        "iat": iat,
        "exp": exp,
    })

    client.cookies["token"] = token

    response = client.get("/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Can not retrieve user"}


async def test_logged_in_user_info__success():
    client = TestClient(app)

    with dal.get_session_ctx() as session:
        db_user = session.query(User).first()

    user_payload = user_schemas.UserRedisPayload.from_orm(db_user)
    token = await redis_utils.store_payload(user_payload, redis_dal)

    client.cookies["token"] = token

    response = client.get("/me")

    assert response.status_code == 200
    assert response.json() == {"id": 1, "username": "client1"}

    await redis_utils.delete_key(user_payload.id, redis_dal)


# /logout Tests
# --------------
def test_logout__token_not_found():
    client = TestClient(app)

    response = client.post("/logout")

    assert response.status_code == 401
    assert response.json() == {"detail": "You are not logged in"}
    assert "token" not in response.cookies.keys()


def test_logout__token_expired():
    client = TestClient(app)

    json_data = {
        "username": "user1",
        "password": "secret",
    }

    db_user = User(
        username=json_data["username"], password=json_data["password"])

    with dal.get_session_ctx() as session:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    sub = str(db_user.id)
    iat = datetime.now().timestamp()
    exp = (datetime.now() - timedelta(minutes=15)).timestamp()

    token = jwt_utils.encode({
        "sub": sub,
        "iat": iat,
        "exp": exp,
    })

    client.cookies["token"] = token

    response = client.post("/logout")

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}

    with dal.get_session_ctx() as session:
        session.delete(db_user)
        session.commit()


def test_logout__invalid_token():
    client = TestClient(app)

    sub = "-1"
    iat = datetime.now().timestamp()
    exp = (datetime.now() + timedelta(minutes=15)).timestamp()

    token = jwt_utils.encode({
        "sub": sub,
        "iat": iat,
        "exp": exp,
    })

    client.cookies["token"] = token

    response = client.post("/logout")

    assert response.status_code == 401
    assert response.json() == {"detail": "Can not retrieve user"}


async def test_logout__success():
    client = TestClient(app)

    json_data = {
        "username": "user1",
        "password": "secret",
    }

    db_user = User(
        username=json_data["username"], password=json_data["password"])

    with dal.get_session_ctx() as session:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    user_payload = user_schemas.UserRedisPayload.from_orm(db_user)
    token = await redis_utils.store_payload(user_payload, redis_dal)

    client.cookies["token"] = token

    response = client.post("/logout")

    assert response.status_code == 204

    with dal.get_session_ctx() as session:
        session.delete(db_user)
        session.commit()
