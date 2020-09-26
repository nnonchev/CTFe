import pytest
from httpx import AsyncClient

from CTFe.main import app
from CTFe.models import (
    Team,
    User,
)
from CTFe.schemas import team_schemas
from CTFe.utils import enums
from CTFe.config import constants
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

        team_details = team_schemas.Details.from_orm(db_team)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get(f"/teams/{db_team.id}")

    assert response.status_code == 200
    assert response.json() == team_details

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
async def test_get_team_by_bane__success():
    team_data = {
        "name": "team1",
    }

    db_team = Team(**team_data)

    with dal.get_session_ctx() as session:
        session.add(db_team)
        session.commit()
        session.refresh(db_team)
        team_details = team_schemas.Details.from_orm(db_team)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.get(f"/teams/name/{db_team.name}")

    assert response.status_code == 200
    assert response.json() == team_details

    with dal.get_session_ctx() as session:
        session.delete(db_team)
        session.commit()


@pytest.mark.asyncio
async def test_get_all_teams__success():
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

        team_details = team_schemas.Details.from_orm(db_team)

        team_details = team_details

    assert response.status_code == 200
    assert response.json() == team_details

    with dal.get_session_ctx() as session:
        session.delete(db_team)
        session.commit()


# Add players to team tests
# --------------------------
@pytest.mark.asyncio
async def test_update_add_player_to_team__team_not_found():
    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.delete(f"/teams/-1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Team not found"}


@pytest.mark.asyncio
async def test_add_player_to_team__team_not_found():
    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.patch(f"/teams/-1/add-player/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Team not found"}


@pytest.mark.asyncio
async def test_add_player_to_team__max_member_number_excceded():
    original_val = constants.MAX_TEAM_MEMBERS
    constants.MAX_TEAM_MEMBERS = 1

    users_data = [
        {
            "username": "user1",
            "password": "secret",
        },
        {
            "username": "user2",
            "password": "secret",
        }
    ]

    team_data = {
        "name": "team 1",
    }

    db_team = Team(**team_data)
    db_user1 = User(**users_data[0])
    db_user2 = User(**users_data[1])

    db_team.players.append(db_user1)

    with dal.get_session_ctx() as session:
        session.add(db_team)
        session.add(db_user1)
        session.add(db_user2)

        session.commit()

        session.refresh(db_team)
        session.refresh(db_user1)
        session.refresh(db_user2)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.patch(f"/teams/{db_team.id}/add-player/{db_user2.id}")

    assert response.status_code == 403
    assert response.json() == {
        "detail": "The team already has the maximum number of members in it"}

    with dal.get_session_ctx() as session:
        session.delete(db_team)
        session.delete(db_user1)
        session.delete(db_user2)

        session.commit()

    constants.MAX_TEAM_MEMBERS = original_val


@pytest.mark.asyncio
async def test_add_player_to_team__player_not_found():
    team_data = {
        "name": "team 1",
    }

    db_team = Team(**team_data)

    with dal.get_session_ctx() as session:
        session.add(db_team)
        session.commit()
        session.refresh(db_team)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.patch(f"/teams/{db_team.id}/add-player/-1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Player not found"}

    with dal.get_session_ctx() as session:
        session.delete(db_team)
        session.commit()


@pytest.mark.asyncio
async def test_add_player_to_team__wrong_user_type():
    user_data = {
        "username": "user1",
        "password": "secret",
    }

    team_data = {
        "name": "team 1",
    }

    db_team = Team(**team_data)
    db_user = User(**user_data)

    db_user.user_type = enums.UserType.ADMIN

    with dal.get_session_ctx() as session:
        session.add(db_team)
        session.add(db_user)

        session.commit()

        session.refresh(db_team)
        session.refresh(db_user)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.patch(f"/teams/{db_team.id}/add-player/{db_user.id}")

    assert response.status_code == 403
    assert response.json() == {
        "detail": f"Only players can be part of teams. { db_user } has user_type: { db_user.user_type }"}

    with dal.get_session_ctx() as session:
        session.delete(db_team)
        session.delete(db_user)

        session.commit()


@pytest.mark.asyncio
async def test_add_player_to_team__player_already_in_team():
    user_data = {
        "username": "user1",
        "password": "secret",
    }

    teams_data = [
        {
            "name": "team 1",
        },
        {
            "name": "team 2",
        },
    ]

    db_team1 = Team(**teams_data[0])
    db_team2 = Team(**teams_data[1])
    db_user = User(**user_data)

    db_team1.players.append(db_user)

    with dal.get_session_ctx() as session:
        session.add(db_team1)
        session.add(db_team2)
        session.add(db_user)

        session.commit()

        session.refresh(db_team1)
        session.refresh(db_team2)
        session.refresh(db_user)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.patch(f"/teams/{db_team1.id}/add-player/{db_user.id}")

    assert response.status_code == 403
    assert response.json() == {
        "detail": f"Player { db_user } is already part of a team"}

    with dal.get_session_ctx() as session:
        session.delete(db_team1)
        session.delete(db_team2)
        session.delete(db_user)

        session.commit()


@pytest.mark.asyncio
async def test_add_player_to_team__success():
    users_data = [
        {
            "username": "user1",
            "password": "secret",
        },
        {
            "username": "user2",
            "password": "secret",
        }
    ]

    team_data = {
        "name": "team 1",
    }

    db_team = Team(**team_data)
    db_user1 = User(**users_data[0])
    db_user2 = User(**users_data[1])

    db_team.players.append(db_user1)

    with dal.get_session_ctx() as session:
        session.add(db_team)
        session.add(db_user1)
        session.add(db_user2)

        session.commit()

        session.refresh(db_team)
        session.refresh(db_user1)
        session.refresh(db_user2)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.patch(f"/teams/{db_team.id}/add-player/{db_user2.id}")

    with dal.get_session_ctx() as session:
        session.add(db_team)
        session.refresh(db_team)

        team_details = team_schemas.Details.from_orm(db_team)

    assert response.status_code == 200
    assert response.json() == team_details

    with dal.get_session_ctx() as session:
        session.delete(db_team)
        session.delete(db_user1)
        session.delete(db_user2)

        session.commit()


# Remove players to team tests
# --------------------------
@pytest.mark.asyncio
async def test_remove_player_from_team__team_not_found():
    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.patch(f"/teams/-1/remove-player/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Team not found"}


@pytest.mark.asyncio
async def test_remove_player_to_team__player_not_found():
    team_data = {
        "name": "team 1"
    }

    db_team = Team(**team_data)

    with dal.get_session_ctx() as session:
        session.add(db_team)
        session.commit()
        session.refresh(db_team)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.patch(f"/teams/{db_team.id}/remove-player/-1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Player not found"}

    with dal.get_session_ctx() as session:
        session.delete(db_team)
        session.commit()


@pytest.mark.asyncio
async def test_remove_player_to_team__player_not_found():
    team_data = {
        "name": "team 1",
    }

    db_team = Team(**team_data)

    with dal.get_session_ctx() as session:
        session.add(db_team)
        session.commit()
        session.refresh(db_team)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.patch(f"/teams/{db_team.id}/remove-player/-1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Player not found"}

    with dal.get_session_ctx() as session:
        session.delete(db_team)
        session.commit()


@pytest.mark.asyncio
async def test_remove_player_to_team__player_not_part_of_the_team():
    team_data = {
        "name": "team 1",
    }

    user_data = {
        "username": "user1",
        "password": "secret",
    }

    db_team = Team(**team_data)
    db_user = User(**user_data)

    with dal.get_session_ctx() as session:
        session.add(db_team)
        session.add(db_user)

        session.commit()

        session.refresh(db_team)
        session.refresh(db_user)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.patch(f"/teams/{db_team.id}/remove-player/{db_user.id}")

    assert response.status_code == 403
    assert response.json() == {
        "detail": f"Player { db_user } is not part of this team"}

    with dal.get_session_ctx() as session:
        session.delete(db_team)
        session.delete(db_user)

        session.commit()


@pytest.mark.asyncio
async def test_remove_player_to_team__success():
    user_data = {
        "username": "user1",
        "password": "secret",
    }

    team_data = {
        "name": "team 1",
    }

    db_team = Team(**team_data)
    db_user = User(**user_data)

    db_team.players.append(db_user)

    with dal.get_session_ctx() as session:
        session.add(db_team)
        session.add(db_user)

        session.commit()

        session.refresh(db_team)
        session.refresh(db_user)

    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.patch(f"/teams/{db_team.id}/remove-player/{db_user.id}")

    with dal.get_session_ctx() as session:
        session.add(db_team)
        session.refresh(db_team)

        team_details = team_schemas.Details.from_orm(db_team)

    assert response.status_code == 200
    assert response.json() == team_details

    with dal.get_session_ctx() as session:
        session.delete(db_team)
        session.delete(db_user)

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
