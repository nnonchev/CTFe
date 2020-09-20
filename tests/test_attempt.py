import io
import os

import pytest
from httpx import AsyncClient
from sqlalchemy import and_

from CTFe.main import app
from CTFe.models import (
    Attempt,
    Team,
    Challenge,
)
from CTFe.schemas import attempt_schemas
from CTFe.config import constants
from . import (
    dal,
    BASE_URL,
)


# Create attempt tests
# ------------------
@pytest.mark.asyncio
async def test_create_attempt__team_not_found():
    attempt_data = {
        "flag": "flag1",
        "team_id": -1,
        "challenge_id": -1,
    }

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.post("/attempts/", json=attempt_data)

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Team not found"}


@pytest.mark.asyncio
async def test_create_attempt__challenge_not_found():
    team_data = {
        "name": "team1",
    }

    db_team = Team(**team_data)

    with dal.get_session_ctx() as session:
        session.add(db_team)
        session.commit()
        session.refresh(db_team)

        attempt_data = {
            "flag": "flag1",
            "team_id": db_team.id,
            "challenge_id": -1,
        }

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.post("/attempts/", json=attempt_data)

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Challenge not found"}

    with dal.get_session_ctx() as session:
        session.delete(db_team)
        session.commit()


@pytest.mark.asyncio
async def test_create_attempt__success():
    team_data = {
        "name": "team1",
    }

    challenge_data = {
        "name": "attempt1",
        "description": "Some description",
        "flag": "secret flag",
        "file_name": None,
    }

    db_team = Team(**team_data)
    db_challenge = Challenge(**challenge_data)

    with dal.get_session_ctx() as session:
        session.add(db_team)
        session.add(db_challenge)

        session.commit()

        session.refresh(db_team)
        session.refresh(db_challenge)

        attempt_data = {
            "flag": "flag1",
            "team_id": db_team.id,
            "challenge_id": db_challenge.id,
        }

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.post("/attempts/", json=attempt_data)

    with dal.get_session_ctx() as session:
        db_attempt = (
            session
            .query(Attempt)
            .filter(
                and_(
                    Attempt.flag == attempt_data["flag"],
                    Attempt.team_id == attempt_data["team_id"],
                    Attempt.challenge_id == attempt_data["challenge_id"],
                )
            )
            .first()
        )

        attempt_details = attempt_schemas.AttemptDetails.from_orm(db_attempt)

    assert response.status_code == 200
    assert response.json() == attempt_details

    with dal.get_session_ctx() as session:
        session.delete(db_attempt)
        session.delete(db_challenge)
        session.delete(db_team)

        session.commit()


# Get attempt tests
# ---------------
@pytest.mark.asyncio
async def test_get_attempt__not_found():
    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get("/attempts/-1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Attempt not found"}


@pytest.mark.asyncio
async def test_get_attempt__success():
    team_data = {
        "name": "team1",
    }

    challenge_data = {
        "name": "attempt1",
        "description": "Some description",
        "flag": "secret flag",
        "file_name": None,
    }

    db_team = Team(**team_data)
    db_challenge = Challenge(**challenge_data)

    with dal.get_session_ctx() as session:
        session.add(db_team)
        session.add(db_challenge)

        session.flush()

        attempt_data = {
            "flag": "flag1",
            "team_id": db_team.id,
            "challenge_id": db_challenge.id,
        }

        db_attempt = Attempt(**attempt_data)
        session.add(db_attempt)

        session.commit()

        session.refresh(db_team)
        session.refresh(db_challenge)
        session.refresh(db_attempt)

        attempt_details = attempt_schemas.AttemptDetails.from_orm(db_attempt)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get(f"/attempts/{db_attempt.id}")

    assert response.status_code == 200
    assert response.json() == attempt_details

    with dal.get_session_ctx() as session:
        session.delete(db_attempt)
        session.delete(db_challenge)
        session.delete(db_team)

        session.commit()


@pytest.mark.asyncio
async def test_get_all_attempts__success():
    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get("/attempts/")

    assert response.status_code == 200
    assert response.json() == []


# Update attempt tests
# ------------------
@pytest.mark.asyncio
async def test_update_attempt__not_found():
    attempt_data = {}

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.put("/attempts/-1", json=attempt_data)

    assert response.status_code == 404
    assert response.json() == {"detail": "Attempt not found"}


@pytest.mark.asyncio
async def test_update_attempt__success():
    team_datas = [
        {
            "name": "team1",
        },
        {
            "name": "team2",
        },
    ]

    challenge_datas = [
        {
            "name": "attempt1",
            "description": "Some description",
            "flag": "secret flag",
            "file_name": None,
        },
        {
            "name": "attempt2",
            "description": "Some description",
            "flag": "secret flag",
            "file_name": None,
        },
    ]

    db_team1 = Team(**team_datas[0])
    db_team2 = Team(**team_datas[1])

    db_challenge1 = Challenge(**challenge_datas[0])
    db_challenge2 = Challenge(**challenge_datas[1])

    with dal.get_session_ctx() as session:
        session.add(db_team1)
        session.add(db_team2)

        session.add(db_challenge1)
        session.add(db_challenge2)

        session.flush()

        old_attempt_data = {
            "flag": "flag1",
            "team_id": db_team1.id,
            "challenge_id": db_challenge1.id,
        }

        new_attempt_data = {
            "flag": "flag2",
            "team_id": db_team2.id,
            "challenge_id": db_challenge2.id,
        }

        db_attempt = Attempt(**old_attempt_data)
        session.add(db_attempt)

        session.commit()

        session.refresh(db_team1)
        session.refresh(db_team2)
        session.refresh(db_challenge1)
        session.refresh(db_challenge2)
        session.refresh(db_attempt)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.put(f"/attempts/{db_attempt.id}", json=new_attempt_data)

    with dal.get_session_ctx() as session:
        session.add(db_attempt)
        session.refresh(db_attempt)

        attempt_details = attempt_schemas.AttemptDetails.from_orm(db_attempt)

    assert response.status_code == 200
    assert response.json() == attempt_details

    with dal.get_session_ctx() as session:
        session.delete(db_attempt)
        session.delete(db_challenge1)
        session.delete(db_challenge2)
        session.delete(db_team1)
        session.delete(db_team2)

        session.commit()


# Delete attempt tests
# ------------------
@pytest.mark.asyncio
async def test_delete_attempt__not_found():
    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.delete(f"/attempts/-1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Attempt not found"}


@pytest.mark.asyncio
async def test_delete_attempt__success():
    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get("/attempts/-1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Attempt not found"}


@pytest.mark.asyncio
async def test_get_attempt__success():
    team_data = {
        "name": "team1",
    }

    challenge_data = {
        "name": "attempt1",
        "description": "Some description",
        "flag": "secret flag",
        "file_name": None,
    }

    db_team = Team(**team_data)
    db_challenge = Challenge(**challenge_data)

    with dal.get_session_ctx() as session:
        session.add(db_team)
        session.add(db_challenge)

        session.flush()

        attempt_data = {
            "flag": "flag1",
            "team_id": db_team.id,
            "challenge_id": db_challenge.id,
        }

        db_attempt = Attempt(**attempt_data)
        session.add(db_attempt)

        session.commit()

        session.refresh(db_team)
        session.refresh(db_challenge)
        session.refresh(db_attempt)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.delete(f"/attempts/{db_attempt.id}")

    assert response.status_code == 204

    with dal.get_session_ctx() as session:
        session.delete(db_challenge)
        session.delete(db_team)

        session.commit()
