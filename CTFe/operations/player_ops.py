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


def create_team(
    session: Session,
    db_player: User,
    db_team: Team,
) -> User:
    """ Create team and assign player as the captain """

    db_player.team = db_team

    session.commit()
    session.refresh(db_player)

    return db_player
