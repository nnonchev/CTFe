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
from CTFe.models import Team
from CTFe.schemas import team_schemas
from CTFe.operations import team_ops


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
    if team_ops.read_team_by_(session, conditions):
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

    db_team = team_ops.read_team_by_(session, conditions)

    if db_team is None:
        raise HTTPException(
            status_code=404,
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

    db_team = team_ops.read_team_by_(session, conditions)

    if db_team is None:
        raise HTTPException(
            status_code=404,
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

    db_team = tema_ops.read_team_by_(session, conditions)

    db_team = team_ops.update_team(session, db_team, team_update)
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

    db_team = team_ops.read_team_by_(session, conditions)

    if db_team is None:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    team_ops.delete_team(session, db_team)
