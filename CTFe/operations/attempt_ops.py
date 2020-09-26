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
    delete_record,
)
from CTFe.models import Attempt
from CTFe.schemas import attempt_schemas


def create_attempt(
    session: Session,
    attempt_create: attempt_schemas.Create,
) -> Attempt:
    """ Create attempt record """

    db_attempt = create_record(session, Attempt, attempt_create)

    return db_attempt


def query_attempts_by_(
    session: Session,
    conditions: Optional[BooleanClauseList] = and_(),
) -> Query:
    """ Query attempt records """

    query_attempts = query_records(session, Attempt, conditions)

    return query_attempts


def delete_attempt(
    session: Session,
    db_attempt: Attempt,
):
    """ Delete attempt record """

    delete_record(session, db_attempt)
