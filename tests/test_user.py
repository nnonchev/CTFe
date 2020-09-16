from fastapi.testclient import TestClient

from CTFe.main import app
from CTFe.models import User
from CTFe.schemas import user_schemas
from CTFe.utils import (
    enums,
    redis_utils,
)
from . import dal


def test_create_user__no_token():
    client = TestClient(app)

    json_data = {
        "username": "user1",
        "password": "secret",
    }

    response = client.post("/users/", json=json_data)

    assert response.status_code == 401
    assert response.json() == {"detail": "You are not logged in"}


async def test_create_user__incorrect_user_type():
    client = TestClient(app)

    json_data = {
        "username": "player1",
        "password": "secret",
    }

    db_admin = User(username="admin1", password="secret")
    db_admin.user_type = enums.UserType.ADMIN

    db_player = User(username="player1", password="secret")

    with dal.get_session_ctx() as session:
        session.add(db_admin)
        session.add(db_player)

        session.commit()

        session.refresh(db_admin)
        session.refresh(db_player)

    user_payload = user_schemas.UserRedisPayload.from_orm(db_player)
    token = await redis_utils.store_payload(user_payload, redis_dal)

    client.cookies["token"] = token

    response = client.post("/users/", json=json_data)
    assert response.status_code == 401
    assert response.json() == {"detail": "You don't have the correct access"}

    with dal.get_session_ctx() as session:
        session.delete(db_admin)
        session.delete(db_player)

        session.commit()
