from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import (
    Session,
    Query,
)
from sqlalchemy.sql.expression import BooleanClauseList

from CTFe.operations.CRUD_ops import (
    create_record,
    query_records,
    update_record,
    delete_record,
)
from CTFe.models import (
    Team,
    User,
)
from CTFe.schemas import team_schemas


def create_team(
    session: Session,
    team_create: team_schemas.Create,
) -> Team:
    """ Create team record """

    db_team = create_record(session, Team, team_create)

    return db_team


def query_teams_by_(
    session: Session,
    conditions: Optional[BooleanClauseList] = and_(),
) -> Query:
    """ Query team records """

    query_teams = query_records(session, Team, conditions)

    return query_teams


def update_team(
    session: Session,
    db_team: Team,
    team_update: team_schemas.Update,
) -> Team:
    """ Update team record """

    db_team = update_record(session, db_team, team_update)

    return db_team


def add_player(
    session: Session,
    db_team: Team,
    player: User,
) -> Team:
    """ Add player to team """

    db_team.players.append(player)

    db_team = update_record(session, db_team)

    return db_team


def remove_player(
    session: Session,
    db_team: Team,
    player: User,
) -> Team:
    """ Remove player from team """

    db_team.players.remove(player)

    team_update = update_record(session, db_team)

    return db_team


def delete_team(
    session: Session,
    db_team: Team,
):
    """ Delete team record """

    delete_record(session, db_team)
