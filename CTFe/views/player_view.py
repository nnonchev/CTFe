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
from CTFe.utils import enums


router = APIRouter()


@router.get("/{id}", response_model=player_schemas.Details)
async def get_player(
    *,
    id: int,
    session: Session = Depends(dal.get_session)
) -> player_schemas.Details:
    """ Retrieve a player record from DB """
    conditions = and_(
        User.id == id,
    )

    db_player = player_ops.query_players_by_(session, conditions).first()

    if db_player is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )

    return db_player


@router.get("/username/{username}", response_model=player_schemas.Details)
async def get_player_by_username(
    *,
    username: str,
    session: Session = Depends(dal.get_session)
) -> player_schemas.Details:
    """ Retrieve a player record from DB """

    conditions = and_(
        User.username == username,
    )

    db_player = player_ops.query_players_by_(session, conditions).first()

    if db_player is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )

    return db_player


@router.get("/", response_model=List[player_schemas.Details])
async def get_all_players(
    session: Session = Depends(dal.get_session)
) -> List[player_schemas.Details]:
    """ Retreive multiple players records from DB """

    db_players = player_ops.query_players_by_(session).all()

    return db_players


@router.put("/", response_model=player_schemas.Details)
async def update_player(
    *,
    player_update: player_schemas.Update,
    db_player: User = Depends(auth_ops.get_current_user),
    session: Session = Depends(dal.get_session)
) -> player_schemas.Details:
    """ Update player record from DB """

    db_player = player_ops.update_player(session, db_player, player_update)

    return db_player


@router.delete("/", status_code=204)
def delete_player(
    *,
    db_player: User = Depends(auth_ops.get_current_user),
    session: Session = Depends(dal.get_session)
):
    """ Delete player record from DB """

    player_ops.delete_player(session, db_player)
