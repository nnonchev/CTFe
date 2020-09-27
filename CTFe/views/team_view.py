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
