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
from CTFe.models import User
from CTFe.schemas import user_schemas


def create_user(
    session: Session,
    user_create: user_schemas.Create,
) -> User:
    """ Create user record """

    db_user = create_record(session, User, user_create)

    return db_user


def query_users_by_(
    session: Session,
    conditions: Optional[BooleanClauseList] = and_(),
) -> Query:
    """ Query user records """

    query_users = query_records(session, User, conditions)

    return query_users


def update_user(
    session: Session,
    db_user: User,
    user_update: user_schemas.Update,
) -> User:
    """ Update user record """

    db_user = update_record(session, db_user, user_update)

    return db_user


def delete_user(
    session: Session,
    db_user: User,
):
    """ Delete user record """

    delete_record(session, db_user)
