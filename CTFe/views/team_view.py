from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from CTFe.config import constants
from CTFe.config.database import dal
from CTFe.utils import enums
from CTFe.operations import (
    team_ops,
    user_ops,
)
from CTFe.models import (
    Team,
    User,
)
from CTFe.schemas import team_schemas


router = APIRouter()


@router.post("/", response_model=team_schemas.Details)
async def create_team(
    *,
    team_create: team_schemas.Create,
    session: Session = Depends(dal.get_session),
) -> team_schemas.Details:
    """ Create new team DB record """

    # Make sure unique fields are not already used
    conditions = and_(
        Team.name == team_create.name,
    )

    db_team = team_ops.query_teams_by_(session, conditions).first()

    if db_team is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The name: { team_create.name } is already taken",
        )

    db_team = team_ops.create_team(session, team_create)

    return db_team


@router.get("/{id}", response_model=team_schemas.Details)
async def get_team(
    *,
    id: int,
    session: Session = Depends(dal.get_session)
) -> team_schemas.Details:
    """ Get team record from DB """

    conditions = and_(
        Team.id == id,
    )

    db_team = team_ops.query_teams_by_(session, conditions).first()

    if db_team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    return db_team


@router.get("/name/{name}", response_model=team_schemas.Details)
async def get_team_by_name(
    *,
    name: str,
    session: Session = Depends(dal.get_session)
) -> team_schemas.Details:
    """ Get team record from DB """

    conditions = and_(
        Team.name == name,
    )

    db_team = team_ops.query_teams_by_(session, conditions).first()

    if db_team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    return db_team


@router.get("/", response_model=List[team_schemas.Details])
async def get_all_teams(
    *,
    session: Session = Depends(dal.get_session)
) -> List[team_schemas.Details]:
    """ Get all team records from DB """

    db_teams = team_ops.query_teams_by_(session).all()

    return db_teams


@router.put("/{id}", response_model=team_schemas.Details)
async def update_team(
    *,
    id: int,
    team_update: team_schemas.Update,
    session: Session = Depends(dal.get_session)
) -> team_schemas.Details:
    """ Update team record from DB """

    conditions = and_(
        Team.id == id,
    )

    db_team = team_ops.query_teams_by_(session, conditions).first()

    if db_team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    db_team = team_ops.update_team(session, db_team, team_update)

    return db_team


@router.delete("/{id}", status_code=204)
async def delete_team(
    *,
    id: int,
    session: Session = Depends(dal.get_session)
):
    """ Delete team record from DB """

    conditions = and_(
        Team.id == id,
    )

    db_team = team_ops.query_teams_by_(session, conditions).first()

    if db_team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    team_ops.delete_team(session, db_team)


@router.patch("/{id}/add-player/{player_id}", response_model=team_schemas.Details)
def add_player(
    *,
    id: int,
    player_id: int,
    session: Session = Depends(dal.get_session)
) -> team_schemas.Details:
    """ Add player to a team """

    # Find the team
    conditions = and_(
        Team.id == id,
    )

    db_team = team_ops.query_teams_by_(session, conditions).first()

    # Team not found
    if db_team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    # Find the user
    conditions = and_(
        User.id == player_id,
        User.user_type == enums.UserType.PLAYER,
    )

    db_user = user_ops.query_users_by_(session, conditions).first()

    # User not found
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Team is full
    if len(db_team.players) >= constants.MAX_TEAM_MEMBERS:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="The team has the maximum number of members in it"
        )

    # User is already part of another team
    if db_user.team is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Player { db_user } is already part of a team",
        )

    db_team = team_ops.add_player(session, db_team, db_player)

    return db_team


@router.patch("/{id}/remove-player/{player_id}", response_model=team_schemas.Details)
def remove_player(
    *,
    id: int,
    player_id: int,
    session: Session = Depends(dal.get_session)
) -> team_schemas.Details:
    """ Remove player from a team """

    # Find the team
    conditions = and_(
        Team.id == id,
    )

    db_team = team_ops.query_teams_by_(session, conditions).first()

    # Team not found
    if db_team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    # Find the user
    conditions = and_(
        User.id == player_id,
        User.user_type == enums.UserType.PLAYER,
    )

    db_user = user_ops.query_users_by_(session, conditions).first()

    # User not found
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # User is not part of the current team
    if db_user.team_id != db_team.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Player { db_user } is not part of this team",
        )

    db_team = team_ops.remove_player(session, db_team, db_user)

    return db_team
