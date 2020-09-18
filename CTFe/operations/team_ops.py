from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import (
    and_,
    BooleanClauseList,
)

from CTFe.models import (
    Team,
    User,
)
from CTFe.schemas import team_schemas


def create_team(
    session: Session,
    team_create: team_schemas.TeamCreate,
) -> Team:
    """ Insert a team record in DB """
    db_team = Team(**team_create.dict())

    session.add(db_team)
    session.commit()
    session.refresh(db_team)

    return db_team
    

def read_teams_by_(
    session: Session,
    conditions: BooleanClauseList,
) -> Team:
    """ Query DB for a team based on multiple queries """
    return session.query(Team).filter(conditions)


def update_team(
    session: Session,
    db_team: Team,
    team_update: team_schemas.TeamUpdate,
) -> Team:
    """ Update team record in DB """

    # Cast to TeamUpdate pydantic model
    team_updated = (
        team_schemas.TeamUpdate.from_orm(db_team)
    )

    # Update the new fields
    team_data = team_updated.copy(
        update=team_update.dict(exclude_unset=True),
    )

    # Update fields
    (
        session
        .query(Team)
        .filter(Team.id == db_team.id)
        .update(team_data.dict())
    )

    session.commit()
    session.refresh(db_team)

    return db_team


def add_player(
    session: Session,
    db_team: Team,
    player: User,
) -> Team:
    db_team.players.append(player)

    session.add(db_team)
    session.commit()
    session.refresh(db_team)

    return db_team


def remove_player(
    session: Session,
    db_team: Team,
    player: User,
) -> Team:
    db_team.players.remove(player)

    session.add(db_team)
    session.commit()
    session.refresh(db_team)

    return db_team


def delete_team(
    session: Session,
    db_team: Team,
):
    session.delete(db_team)
    session.commit()
