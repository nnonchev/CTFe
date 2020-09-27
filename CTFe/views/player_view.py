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
    User,
    Team,
)
from CTFe.schemas import (
    player_schemas,
    team_schemas,
)
from CTFe.operations import (
    player_ops,
    auth_ops,
    user_ops,
    team_ops,
)
from CTFe.utils import enums
from CTFe.config import constants


router = APIRouter()


@router.get("/list-invites", response_model=player_schemas.Invites)
async def list_invites(
    *,
    db_player: User = Depends(auth_ops.get_current_user),
    session: Session = Depends(dal.get_session),
) -> player_schemas.Invites:
    """ List all the invites the player has recieved """

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


@router.post("/create-team", response_model=player_schemas.Details)
def create_team(
    *,
    team_create: team_schemas.Create,
    db_player: User = Depends(auth_ops.get_current_user),
    session: Session = Depends(dal.get_session),
) -> player_schemas.Details:
    """ Create team and assign this player as the captain """

    # Player is not part of another team
    if db_player.team is not None:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="You are already part of a team"
        )

     # Team name is already taken
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
    db_player = player_ops.create_team(session, db_player, db_team)

    return db_player


@router.patch("/quit-team", status_code=204)
def quit_team(
    *,
    db_player: User = Depends(auth_ops.get_current_user),
    session: Session = Depends(dal.get_session),
) -> player_schemas.Details:
    """ Quit team and assign the next member as captain or delete team if no other members """

    db_team = db_player.team

    # Team doesn't exist
    if db_team is None:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="You are not part of a team",
        )

    if len(db_team.players) <= 1:
        team_ops.delete_team(session, db_team)
    else:
        player_ops.quit_team(session, db_player)


@router.patch("/invite-player/{player_id}", status_code=204)
def invite_player(
    *,
    player_id: int,
    db_player: User = Depends(auth_ops.get_current_user),
    session: Session = Depends(dal.get_session),
) -> player_schemas.Details:
    """ Invite player to join the team """

    db_team = db_player.team

    # Team doesn't exist
    if db_team is None:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="You are not part of a team",
        )

    # The team is full
    if len(db_team.players) >= constants.MAX_TEAM_MEMBERS:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="The team is full",
        )

    conditions = and_(
        User.id == player_id,
    )

    db_new_player = player_ops.query_players_by_(session, conditions).first()

    # Wrong player id
    if db_new_player is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )

    # New player has already been invited
    if db_team in db_new_player.team_invites:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail=f"This player has already been invited",
        )


    # New player is part of another team
    if db_new_player.team is not None:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Player is already part of a team",
        )

    player_ops.invite_player(session, db_new_player, db_team)


@router.patch("/delete-invite/{player_id}", status_code=204)
def delete_invite(
    *,
    player_id: int,
    db_player: User = Depends(auth_ops.get_current_user),
    session: Session = Depends(dal.get_session),
) -> player_schemas.Details:
    """ Delete player invitation to join the team """

    db_team = db_player.team

    conditions = and_(
        User.id == player_id,
    )

    db_new_player = player_ops.query_players_by_(session, conditions).first()

    # Player not found
    if db_new_player is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )

    # Team doesn't exist
    if db_team is None:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="You are not part of a team",
        )

    # The team hasn't invited the player
    if db_new_player not in db_team.player_invites:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail=f"This player has not been invited",
        )

    player_ops.delete_invitation(session, db_new_player, db_team)


@router.patch("/accept-invite/{team_id}", status_code=204)
def accept_invite(
    *,
    team_id: int,
    db_player: User = Depends(auth_ops.get_current_user),
    session: Session = Depends(dal.get_session),
) -> player_schemas.Details:
    """ Accept player invitation to join the team """

    # User is already in a team
    if db_player.team is not None:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="You are already part of a team",
        )

    conditions = and_(
        Team.id == team_id,
        Team.player_invites.any(id = db_player.id),
    )

    db_team = team_ops.query_teams_by_(session, conditions).first()

    # Team doesn't exist
    if db_team is None:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="The team is not found",
        )

    # The team is full
    if len(db_team.players) >= constants.MAX_TEAM_MEMBERS:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="The team is full",
        )

    player_ops.accept_invite(session, db_player, db_team)
