from typing import (
    List,
    Optional,
)

from sqlalchemy import and_
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    Cookie,
    status,
    HTTPException,
)

from CTFe.config.database import dal
from CTFe.models import (
    Team,
    User,
)
from CTFe.schemas import team_schemas
from CTFe.operations import (
    team_ops,
    user_ops,
)
from CTFe.utils import enums
from CTFe.config import constants


router = APIRouter()


@router.post("/", response_model=team_schemas.TeamDetails)
async def create_team(
    *,
    team_create: team_schemas.TeamCreate,
    session: Session = Depends(dal.get_session),
) -> team_schemas.TeamDetails:
    """ Create new team DB record """
    conditions = and_(
        Team.name == team_create.name,
    )

    # Check if a team record with the same unique fields already exists
    if team_ops.read_team_by_(session, conditions).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The name: { team_create.name } is already taken"
        )

    db_team = team_ops.create_team(session, team_create)

    return db_team


@router.get("/{id}", response_model=team_schemas.TeamDetails)
async def get_team(
    *,
    id: int,
    session: Session = Depends(dal.get_session)
) -> team_schemas.TeamDetails:
    """ Retrieve a team record from DB """
    conditions = and_(
        Team.id == id,
    )

    db_team = team_ops.read_team_by_(session, conditions).first()

    if db_team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    return db_team


@router.get("/name/{name}", response_model=team_schemas.TeamDetails)
async def get_team_by_name(
    *,
    name: str,
    session: Session = Depends(dal.get_session)
) -> team_schemas.TeamDetails:
    """ Retrieve a team record from DB """
    conditions = and_(
        Team.name == name,
    )

    db_team = team_ops.read_team_by_(session, conditions).first()

    if db_team is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    return db_team


@router.get("/", response_model=List[team_schemas.TeamDetails])
async def get_all_teams(
    session: Session = Depends(dal.get_session)
) -> List[team_schemas.TeamDetails]:
    """ Retreive multiple team records from DB """
    db_teams = team_ops.read_teams_by_(session, and_())
    return db_teams.all()


@router.put("/{id}", response_model=team_schemas.TeamDetails)
async def update_team(
    *,
    id: int,
    team_update: team_schemas.TeamUpdate,
    session: Session = Depends(dal.get_session)
) -> team_schemas.TeamDetails:
    """ Update a team record from DB """
    conditions = and_(
        Team.id == id,
    )

    db_team = team_ops.read_team_by_(session, conditions).first()

    if db_team is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    db_team = team_ops.update_team(session, db_team, team_update)
    return db_team


@router.patch("/{id}/add-player/{player_id}", response_model=team_schemas.TeamDetails)
def add_player(
    *,
    id: int,
    player_id: int,
    session: Session = Depends(dal.get_session)
) -> team_schemas.TeamDetails:
    get_team_conditions = and_(
        Team.id == id,
    )

    db_team = team_ops.read_team_by_(session, get_team_conditions).first()

    # Check if team exists
    if db_team is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    # Check if the already added players don't exceed the max team members constnat
    if len(db_team.players) >= constants.MAX_TEAM_MEMBERS:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="The team already has the maximum number of members in it"
        )

    get_player_conditions = and_(
        User.id == player_id
    )

    db_player = user_ops.read_user_by_(session, get_player_conditions).first()

    # Check if user exists
    if db_player is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )

    # Check if user is of user_type player
    if db_player.user_type != enums.UserType.PLAYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Only players can be part of teams. { db_player } has user_type: { db_player.user_type }",
        )

    # Check if user hasn't already joined another team
    if db_player.team is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Player { db_player } is already part of a team",
        )

    db_team = team_ops.add_player(session, db_team, db_player)

    return db_team


@router.patch("/{id}/remove-player/{player_id}", response_model=team_schemas.TeamDetails)
def remove_player(
    *,
    id: int,
    player_id: int,
    session: Session = Depends(dal.get_session)
) -> team_schemas.TeamDetails:
    get_team_conditions = and_(
        Team.id == id,
    )

    db_team = team_ops.read_team_by_(session, get_team_conditions).first()

    # Check if team exists
    if db_team is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    get_player_conditions = and_(
        User.id == player_id
    )

    db_player = user_ops.read_user_by_(session, get_player_conditions).first()

    # Check if user exists
    if db_player is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )

    # Check if user is part of the current team
    if db_player.team_id != db_team.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Player { db_player } is not part of this team",
        )

    db_team = team_ops.remove_player(session, db_team, db_player)

    return db_team


@router.delete("/{id}", status_code=204)
def delete_user(
    *,
    id: int,
    session: Session = Depends(dal.get_session)
):
    """ Delete a team record from DB """
    conditions = and_(
        Team.id == id,
    )

    db_team = team_ops.read_team_by_(session, conditions).first()

    if db_team is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    team_ops.delete_team(session, db_team)
