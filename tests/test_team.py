import pytest
from httpx import AsyncClient

from CTFe.main import app
from CTFe.models import Team
from CTFe.schemas import team_schemas
from . import (
    dal,
    BASE_URL,
)


# Create team tests
# ------------------
@pytest.mark.asyncio
async def test_create_team__already_exists():
    team_data = {
        "name": "team1",
    }

    db_team = Team(**team_data)

    with dal.get_session_ctx() as session:
        session.add(db_team)
        session.commit()
        session.refresh(db_team)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.post("/teams/", json=team_data)

    assert response.status_code == 409
    assert response.json() == {
        "detail": f"The name: { team_data['name'] } is already taken"}

    with dal.get_session_ctx() as session:
        session.delete(db_team)
        session.commit()


@pytest.mark.asyncio
async def test_create_team__success():
    team_data = {
        "name": "team1",
    }

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.post("/teams/", json=team_data)

    assert response.status_code == 200
    assert "id" in response.json().keys()
    assert ("name", team_data["name"]) in response.json().items()

    with dal.get_session_ctx() as session:
        id = response.json()["id"]
        db_team = session.query(Team).filter(Team.id == id).first()

        session.delete(db_team)
        session.commit()


# Get team tests
# ---------------
@pytest.mark.asyncio
async def test_get_team__not_found():
    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get("/teams/-1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Team not found"}


@pytest.mark.asyncio
async def test_get_team__success():
    team_data = {
        "name": "team1",
    }

    db_team = Team(**team_data)

    with dal.get_session_ctx() as session:
        session.add(db_team)
        session.commit()
        session.refresh(db_team)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get(f"/teams/{db_team.id}")

    assert response.status_code == 200
    assert response.json() == team_schemas.TeamDetails.from_orm(db_team)

    with dal.get_session_ctx() as session:
        session.delete(db_team)
        session.commit()


@pytest.mark.asyncio
async def test_get_team_by_name__not_found():
    name = "team1"

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get(f"/teams/name/{name}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Team not found"}


@pytest.mark.asyncio
async def test_get_team__success():
    team_data = {
        "name": "team1",
    }

    db_team = Team(**team_data)

    with dal.get_session_ctx() as session:
        session.add(db_team)
        session.commit()
        session.refresh(db_team)
        team_details = team_schemas.TeamDetails.from_orm(db_team)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get(f"/teams/name/{db_team.name}")

    assert response.status_code == 200
    assert response.json() == team_details

    with dal.get_session_ctx() as session:
        session.delete(db_team)
        session.commit()


@pytest.mark.asyncio
async def test_get_teams__success():
    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get("/teams/")

    assert response.status_code == 200
    assert response.json() == []


# Update team tests
# ------------------
@pytest.mark.asyncio
async def test_update_team__not_found():
    team_data = {}

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.put(f"/teams/-1", json=team_data)

    assert response.status_code == 404
    assert response.json() == {"detail": "Team not found"}


@pytest.mark.asyncio
async def test_update_team__success():
    user_data = {}

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.put(f"/users/-1", json=user_data)

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_update_team__success():
    team_data = {
        "name": "team old",
    }

    new_team_data = {
        "name": "team new",
    }

    db_team = Team(**team_data)

    with dal.get_session_ctx() as session:
        session.add(db_team)
        session.commit()
        session.refresh(db_team)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.put(f"/teams/{db_team.id}", json=new_team_data)

    with dal.get_session_ctx() as session:
        session.add(db_team)
        session.refresh(db_team)

        team_details = team_schemas.TeamDetails.from_orm(db_team)

    assert response.status_code == 200
    assert response.json() == team_details

    with dal.get_session_ctx() as session:
        session.delete(db_team)
        session.commit()


# Delete team tests
# ------------------
@pytest.mark.asyncio
async def test_delete_team__not_found():
    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.delete(f"/teams/-1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Team not found"}


@pytest.mark.asyncio
async def test_delete_team__success():
    team_data = {
        "name": "team1",
    }

    db_team = Team(**team_data)

    with dal.get_session_ctx() as session:
        session.add(db_team)
        session.commit()
        session.refresh(db_team)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.delete(f"/teams/{db_team.id}")

    assert response.status_code == 204

    with dal.get_session_ctx() as session:
        session.delete(db_team)
        session.commit()
