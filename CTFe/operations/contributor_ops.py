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
from CTFe.models import User
from CTFe.schemas import contributor_schemas
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
