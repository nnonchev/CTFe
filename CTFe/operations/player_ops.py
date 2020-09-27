from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import (
    Session,
    Query,
)
from sqlalchemy.sql.expression import BooleanClauseList

from CTFe.operations.CRUD_ops import (
    query_records,
    update_record,
    delete_record,
)
from CTFe.models import (
    User,
    Team,
)
from CTFe.schemas import player_schemas
from CTFe.utils import enums


def query_players_by_(
    session: Session,
    conditions: Optional[BooleanClauseList] = and_(),
) -> Query:
    """ Query player records """

    conditions = and_(
        User.user_type == enums.UserType.PLAYER,
        conditions,
    )

    query_players = query_records(session, User, conditions)

    return query_players


def update_player(
    session: Session,
    db_player: User,
    player_update: player_schemas.Update,
) -> User:
    """ Update player record """

    db_player = update_record(session, db_player, player_update)

    return db_player


def delete_player(
    session: Session,
    db_player: User,
):
    """ Delete player record """

    delete_record(session, db_player)


def lead_team(
    session: Session,
    db_player: User,
    db_team: Team,
) -> User:
    """ Create team and assign player as the captain """

    db_player.team = db_team

    session.commit()
    session.refresh(db_player)

    return db_player


def quit_team(
    session: Session,
    db_player: User,
) -> User:
    """ Remove player from team """
    db_player.team = None

    session.commit()
    session.refresh(db_player)

    return db_player


def accept_invite(
    session: Session,
    db_player: User,
    db_team: Team,
) -> User:
    """ add player to team """
    db_player.team = db_team
    db_player.team_invites.remove(db_team)

    session.commit()


def invite_player(
    session: Session,
    db_player: User,
    db_team: Team,
):
    """ Invite another player to join the team """

    db_team.player_invites.append(db_player)

    session.commit()


def remove_invitation(
    session: Session,
    db_player: User,
    db_team: Team,
):
    """ Delete invitation for player to join the team """

    db_team.player_invites.remove(db_player)

    session.commit()
