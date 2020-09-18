import pytest
from httpx import AsyncClient

from CTFe.main import app
from CTFe.models import User
from CTFe.schemas import user_schemas
from CTFe.utils import validators
from . import (
    dal,
    BASE_URL,
)


# Create user tests
# ------------------
@pytest.mark.asyncio
async def test_create_user__already_exists():
    app.dependency_overrides[validators.validate_admin] = lambda: None

    user_data = {
        "username": "user1",
        "password": "secret",
    }

    db_user = User(**user_data)

    with dal.get_session_ctx() as session:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.post("/users/", json=user_data)

    assert response.status_code == 409
    assert response.json() == {
        "detail": f"The username: { user_data['username'] } is already taken"}

    with dal.get_session_ctx() as session:
        session.delete(db_user)
        session.commit()

    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_create_user__success():
    app.dependency_overrides[validators.validate_admin] = lambda: None

    user_data = {
        "username": "user1",
        "password": "secret",
    }

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.post("/users/", json=user_data)

    assert response.status_code == 200
    assert "id" in response.json().keys()
    assert ("username", user_data["username"]) in response.json().items()

    with dal.get_session_ctx() as session:
        id = response.json()["id"]
        db_user = session.query(User).filter(User.id == id).first()

        session.delete(db_user)
        session.commit()

    app.dependency_overrides = {}


# Get user tests
# ---------------
@pytest.mark.asyncio
async def test_get_user__not_found():
    app.dependency_overrides[validators.validate_admin] = lambda: None

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get("/users/-1")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_get_user__success():
    app.dependency_overrides[validators.validate_admin] = lambda: None

    user_data = {
        "username": "user1",
        "password": "secret",
    }

    db_user = User(**user_data)

    with dal.get_session_ctx() as session:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get(f"/users/{db_user.id}")

    assert response.status_code == 200
    assert response.json() == user_schemas.UserDetails.from_orm(db_user)

    with dal.get_session_ctx() as session:
        session.delete(db_user)
        session.commit()

    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_get_user_by_username__not_found():
    app.dependency_overrides[validators.validate_admin] = lambda: None

    username = "user1"

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get(f"/users/username/{username}")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_get_user__success():
    app.dependency_overrides[validators.validate_admin] = lambda: None

    user_data = {
        "username": "user1",
        "password": "secret",
    }

    db_user = User(**user_data)

    with dal.get_session_ctx() as session:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get(f"/users/username/{db_user.username}")

    assert response.status_code == 200
    assert response.json() == user_schemas.UserDetails.from_orm(db_user)

    with dal.get_session_ctx() as session:
        session.delete(db_user)
        session.commit()

    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_get_users__success():
    app.dependency_overrides[validators.validate_admin] = lambda: None

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get("/users/")

    assert response.status_code == 200
    assert response.json() == []

    app.dependency_overrides = {}


# Update user tests
# ------------------
@pytest.mark.asyncio
async def test_update_user__not_found():
    app.dependency_overrides[validators.validate_admin] = lambda: None

    user_data = {}

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.put(f"/users/-1", json=user_data)

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_update_user__success2():
    app.dependency_overrides[validators.validate_admin] = lambda: None

    user_data = {
        "username": "user1",
        "password": "secret",
    }

    new_user_data = {
        "user_type": "admin",
        "password": "better_secret",
    }

    db_user = User(**user_data)

    with dal.get_session_ctx() as session:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.put(f"/users/{db_user.id}", json=new_user_data)

    with dal.get_session_ctx() as session:
        session.add(db_user)
        session.refresh(db_user)

    assert response.status_code == 200
    assert response.json() == user_schemas.UserDetails.from_orm(db_user)

    with dal.get_session_ctx() as session:
        session.delete(db_user)
        session.commit()

    app.dependency_overrides = {}


# Delete user tests
# ------------------
@pytest.mark.asyncio
async def test_delete_user__not_found():
    app.dependency_overrides[validators.validate_admin] = lambda: None

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.delete(f"/users/-1")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_delete_user__success():
    app.dependency_overrides[validators.validate_admin] = lambda: None

    user_data = {
        "username": "user1",
        "password": "secret",
    }

    db_user = User(**user_data)

    with dal.get_session_ctx() as session:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.delete(f"/users/{db_user.id}")

    assert response.status_code == 204

    with dal.get_session_ctx() as session:
        session.delete(db_user)
        session.commit()

    app.dependency_overrides = {}
