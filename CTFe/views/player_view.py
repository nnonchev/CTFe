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
from CTFe.models import User
from CTFe.schemas import player_schemas
from CTFe.operations import (
    player_ops,
    auth_ops,
    user_ops,
)


router = APIRouter()


@router.get("/{id}", response_model=player_schemas.PlayerDetails)
async def get_player(
    *,
    id: int,
    session: Session = Depends(dal.get_session)
) -> player_schemas.PlayerDetails:
    """ Retrieve a player record from DB """
    conditions = and_(
        User.id == id,
    )

    db_player = player_ops.read_players_by_(session, conditions).first()

    if db_player is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )

    return db_player


@router.get("/username/{username}", response_model=player_schemas.PlayerDetails)
async def get_player_by_username(
    *,
    username: str,
    session: Session = Depends(dal.get_session)
) -> player_schemas.PlayerDetails:
    """ Retrieve a player record from DB """
    conditions = and_(
        User.username == username,
    )

    db_player = player_ops.read_players_by_(session, conditions).first()

    if db_player is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )

    return db_player


@router.get("/", response_model=List[player_schemas.PlayerDetails])
async def get_all_players(
    session: Session = Depends(dal.get_session)
) -> List[player_schemas.PlayerDetails]:
    """ Retreive multiple players records from DB """
    db_players = player_ops.read_players_by_(session, and_()).all()

    return db_players


# TODO Password is saved as plain text :/
@router.put("/", response_model=player_schemas.PlayerDetails)
async def update_player(
    *,
    db_user: User = Depends(auth_ops.get_current_user),
    player_update: player_schemas.PlayerUpdate,
    session: Session = Depends(dal.get_session)
) -> player_schemas.PlayerDetails:
    """ Update a user record from DB """
    if db_user is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )

    db_user = user_ops.update_user(session, db_user, player_update)

    return db_user


@router.delete("/", status_code=204)
def delete_player(
    *,
    db_user: User = Depends(auth_ops.get_current_user),
    session: Session = Depends(dal.get_session)
):
    """ Delete a user record from DB """
    if db_user is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )

    """ Delete user record from DB """
    user_ops.delete_user(session, db_user)
