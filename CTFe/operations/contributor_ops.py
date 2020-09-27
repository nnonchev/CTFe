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
from CTFe.operations import challenge_ops
from CTFe.models import (
    User,
    Challenge,
)
from CTFe.schemas import (
    contributor_schemas,
    challenge_schemas,
)
from CTFe.utils import enums


def query_contributors_by_(
    session: Session,
    conditions: Optional[BooleanClauseList] = and_(),
) -> Query:
    """ Query contributor records """

    conditions = and_(
        User.user_type == enums.UserType.CONTRIBUTOR,
        conditions,
    )

    query_contributors = query_records(session, User, conditions)

    return query_contributors


def update_contributor(
    session: Session,
    db_contributor: User,
    contributor_update: contributor_schemas.Update,
) -> User:
    """ Update contributor record """

    db_contributor = update_record(session, db_contributor, contributor_update)

    return db_contributor


def delete_contributor(
    session: Session,
    db_contributor: User,
):
    """ Delete contributor record """

    delete_record(session, db_contributor)


def create_challenge(
    session: Session,
    challenge_create: challenge_schemas.Create,
    db_contributor: User
):
    """ Create a challenge and assign contributor to it """

    challenge_create.owner_id = db_contributor.id

    db_challenge = challenge_ops.create_challenge(session, challenge_create)


def remove_challenge(
    session: Session,
    db_challenge: Challenge,
    db_contributor: User,
) -> User:
    """ Remove challenge from contributor """

    db_contributor.challenges.remove(db_challenge)

    session.commit()
    session.refresh(db_contributor)

    return db_contributor
