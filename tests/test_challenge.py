import io
import os

import pytest
from httpx import AsyncClient

from CTFe.main import app
from CTFe.models import Challenge
from CTFe.schemas import challenge_schemas
from CTFe.config import constants
from . import (
    dal,
    BASE_URL,
)


# Create challenge tests
# ------------------
@pytest.mark.asyncio
async def test_create_challenge__already_exists():
    challenge_data = {
        "name": "challenge1",
        "description": None,
        "flag": "secret flag",
        "file_name": None,
    }

    db_challenge = Challenge(**challenge_data)

    with dal.get_session_ctx() as session:
        session.add(db_challenge)
        session.commit()
        session.refresh(db_challenge)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.post("/challenges/", json=challenge_data)

    assert response.status_code == 409
    assert response.json() == {
        "detail": f"The name: { challenge_data['name'] } is already taken"}

    with dal.get_session_ctx() as session:
        session.delete(db_challenge)
        session.commit()


@pytest.mark.asyncio
async def test_create_challenge__success():
    challenge_data = {
        "name": "challenge1",
        "description": None,
        "flag": "secret flag",
        "file_name": None,
    }

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.post("/challenges/", json=challenge_data)

    with dal.get_session_ctx() as session:
        db_challenge = (
            session
            .query(Challenge)
            .filter(Challenge.name == challenge_data["name"])
            .first()
        )

        challenge_details = challenge_schemas.Details.from_orm(
            db_challenge)

    assert response.status_code == 200
    assert response.json() == challenge_details

    with dal.get_session_ctx() as session:
        db_challenge = session.query(Challenge).filter(
            Challenge.id == challenge_details.id).first()

        session.delete(db_challenge)
        session.commit()


# Get challenge tests
# ---------------
@pytest.mark.asyncio
async def test_get_challenge__not_found():
    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get("/challenges/-1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Challenge not found"}


@pytest.mark.asyncio
async def test_get_challenge__success():
    challenge_data = {
        "name": "challenge1",
        "description": None,
        "flag": "secret flag",
        "file_name": None,
    }

    db_challenge = Challenge(**challenge_data)

    with dal.get_session_ctx() as session:
        session.add(db_challenge)
        session.commit()
        session.refresh(db_challenge)

        challenge_details = challenge_schemas.Details.from_orm(
            db_challenge)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get(f"/challenges/{challenge_details.id}")

    assert response.status_code == 200
    assert response.json() == challenge_details

    with dal.get_session_ctx() as session:
        session.delete(db_challenge)
        session.commit()


@pytest.mark.asyncio
async def test_get_challenge_by_name__not_found():
    name = "challenge1"

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get(f"/challenges/name/{name}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Challenge not found"}


@pytest.mark.asyncio
async def test_get_challenge_by_name__success():
    challenge_data = {
        "name": "challenge1",
        "description": None,
        "flag": "secret flag",
        "file_name": None,
    }

    db_challenge = Challenge(**challenge_data)

    with dal.get_session_ctx() as session:
        session.add(db_challenge)
        session.commit()
        session.refresh(db_challenge)

        challenge_details = challenge_schemas.Details.from_orm(
            db_challenge)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get(f"/challenges/name/{db_challenge.name}")

    assert response.status_code == 200
    assert response.json() == challenge_details

    with dal.get_session_ctx() as session:
        session.delete(db_challenge)
        session.commit()


@pytest.mark.asyncio
async def test_get_all_challenges__success():
    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get("/challenges/")

    assert response.status_code == 200
    assert response.json() == []


# Update challenge tests
# ------------------
@pytest.mark.asyncio
async def test_update_challenge__not_found():
    challenge_data = {}

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.put(f"/challenges/-1", json=challenge_data)

    assert response.status_code == 404
    assert response.json() == {"detail": "Challenge not found"}


@pytest.mark.asyncio
async def test_update_challenge__success():
    challenge_data = {
        "name": "challenge old",
        "description": None,
        "flag": "secret flag",
        "file_name": None,
    }

    new_challenge_data = {
        "name": "challenge new",
    }

    db_challenge = Challenge(**challenge_data)

    with dal.get_session_ctx() as session:
        session.add(db_challenge)
        session.commit()
        session.refresh(db_challenge)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.put(f"/challenges/{db_challenge.id}", json=new_challenge_data)

    with dal.get_session_ctx() as session:
        session.add(db_challenge)
        session.refresh(db_challenge)

        challenge_details = challenge_schemas.Details.from_orm(
            db_challenge)

        challenge_details = challenge_details

    assert response.status_code == 200
    assert response.json() == challenge_details

    with dal.get_session_ctx() as session:
        session.delete(db_challenge)
        session.commit()


# Upload file tests
# ------------------
@pytest.mark.asyncio
async def test_upload_file_challenge__not_found():
    files = {
        "challenge_file": (
            "test_file.txt",
            io.StringIO("Goodbye world"),
        )
    }

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.post("/challenges/-1/upload-file", files=files)

    assert response.status_code == 404
    assert response.json() == {"detail": "Challenge not found"}


@pytest.mark.asyncio
async def test_upload_file_challenge__already_uploaded():
    filename = "test_file.txt"

    files = {
        "challenge_file": (
            filename,
            io.StringIO("Goodbye world"),
        )
    }

    challenge_data = {
        "name": "challenge old",
        "description": None,
        "flag": "secret flag",
        "file_name": filename,
    }

    db_challenge = Challenge(**challenge_data)

    with dal.get_session_ctx() as session:
        session.add(db_challenge)
        session.commit()
        session.refresh(db_challenge)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.post(f"/challenges/{db_challenge.id}/upload-file", files=files)

    assert response.status_code == 401
    assert response.json() == {
        "detail": "There is already a file associated with this challenge"}

    filepath = os.path.join(
        constants.UPLOAD_FILE_LOCATION,
        db_challenge.file_name
    )
    assert not os.path.isfile(filepath)

    with dal.get_session_ctx() as session:
        session.delete(db_challenge)
        session.commit()


@pytest.mark.asyncio
async def test_upload_file_challenge__success():
    challenge_data = {
        "name": "challenge old",
        "description": None,
        "flag": "secret flag",
        "file_name": None,
    }

    db_challenge = Challenge(**challenge_data)

    with dal.get_session_ctx() as session:
        session.add(db_challenge)
        session.commit()
        session.refresh(db_challenge)

    files = {
        "challenge_file": (
            "test_file.txt",
            io.StringIO("Goodbye world"),
        )
    }

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.post(f"/challenges/{db_challenge.id}/upload-file", files=files)

    with dal.get_session_ctx() as session:
        session.add(db_challenge)
        session.refresh(db_challenge)

        challenge_update = challenge_schemas.Details.from_orm(
            db_challenge)

    assert response.status_code == 200
    assert response.json() == challenge_update

    filepath = os.path.join(
        constants.UPLOAD_FILE_LOCATION,
        challenge_update.file_name
    )

    assert os.path.isfile(filepath)

    os.remove(filepath)

    with dal.get_session_ctx() as session:
        session.delete(db_challenge)
        session.commit()


# Remove uploaded file tests
# ---------------------------
@pytest.mark.asyncio
async def test_remove_uploaded_file_challenge__not_found():
    files = {
        "challenge_file": (
            "test_file.txt",
            io.StringIO("Goodbye world"),
        )
    }

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.post("/challenges/-1/remove-file", files=files)

    assert response.status_code == 404
    assert response.json() == {"detail": "Challenge not found"}


@pytest.mark.asyncio
async def test_remove_uploaded_file_challenge__remove_null_file():
    files = {
        "challenge_file": (
            "test_file.txt",
            io.StringIO("Goodbye world"),
        )
    }

    challenge_data = {
        "name": "challenge old",
        "description": None,
        "flag": "secret flag",
        "file_name": None,
    }

    db_challenge = Challenge(**challenge_data)

    with dal.get_session_ctx() as session:
        session.add(db_challenge)
        session.commit()
        session.refresh(db_challenge)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.post(f"/challenges/{db_challenge.id}/remove-file", files=files)

    assert response.status_code == 401
    assert response.json() == {
        "detail": "There is no file for this challenge"}

    with dal.get_session_ctx() as session:
        session.delete(db_challenge)
        session.commit()


@pytest.mark.asyncio
async def test_remove_uploaded_file_challenge__success():
    challenge_data = {
        "name": "challenge old",
        "description": None,
        "flag": "secret flag",
        "file_name": "test_file.txt",
    }

    db_challenge = Challenge(**challenge_data)

    with dal.get_session_ctx() as session:
        session.add(db_challenge)
        session.commit()
        session.refresh(db_challenge)

    filepath = os.path.join(
        constants.UPLOAD_FILE_LOCATION,
        db_challenge.file_name
    )

    open(filepath, "w").close()

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.post(f"/challenges/{db_challenge.id}/remove-file")

    with dal.get_session_ctx() as session:
        session.add(db_challenge)
        session.refresh(db_challenge)

        challenge_update = challenge_schemas.Details.from_orm(
            db_challenge)

    assert response.status_code == 200
    assert response.json() == challenge_update

    assert not os.path.isfile(filepath)

    with dal.get_session_ctx() as session:
        session.delete(db_challenge)
        session.commit()


# Delete challenge tests
# ------------------
@pytest.mark.asyncio
async def test_delete_challenge__not_found():
    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.delete(f"/challenges/-1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Challenge not found"}


@pytest.mark.asyncio
async def test_delete_challenge__success():
    challenge_data = {
        "name": "challenge1",
        "description": None,
        "flag": "secret flag",
        "file_name": None,
    }

    db_challenge = Challenge(**challenge_data)

    with dal.get_session_ctx() as session:
        session.add(db_challenge)
        session.commit()
        session.refresh(db_challenge)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.delete(f"/challenges/{db_challenge.id}")

    assert response.status_code == 204

    with dal.get_session_ctx() as session:
        session.delete(db_challenge)
        session.commit()
