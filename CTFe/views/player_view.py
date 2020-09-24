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
from CTFe.utils import (
    enums,
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


@router.patch("/quit-team", response_model=player_schemas.PlayerDetails)
def quit_team(
    *,
    db_user: User = Depends(auth_ops.get_current_user),
    session: Session = Depends(dal.get_session),
) -> player_schemas.PlayerDetails:
    """ Remove current player from team """

    # Check if user is of user_type player
    if not db_user.user_type == enums.UserType.PLAYER:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Only players can quit a team"
        )

    # Check if current user is part of a team
    if db_user.team == None:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="You are not part of any team"
        )

    db_user = player_ops.quit_team(db_user, session)

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
