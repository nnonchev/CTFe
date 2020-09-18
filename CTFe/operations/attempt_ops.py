from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import BooleanClauseList

from CTFe.models import Attempt
from CTFe.schemas import attempt_schemas


def create_attempt(
    session: Session,
    attempt_create: attempt_schemas.AttemptCreate,
) -> Attempt:
    """ Insert an attempt record in DB """
    db_attempt = Attempt(**attempt_create.dict())

    session.add(db_attempt)
    session.commit()
    session.refresh(db_attempt)

    return db_attempt


def read_attempts_by_(
    session: Session,
    conditions: BooleanClauseList,
) -> Attempt:
    """ Query DB for attempt records based on multiple queries """
    return session.query(Attempt).filter(conditions)


def update_attempt(
    session: Session,
    db_attempt: Attempt,
    attempt_update: attempt_schemas.AttemptUpdate,
) -> Attempt:
    """ Update attempt record in DB """

    # Cast to AttemptUpdate pydantic model
    attempt_updated = (
        attempt_schemas.AttemptUpdate.from_orm(db_attempt)
    )

    # Update the new fields
    attempt_data = attempt_updated.copy(
        update=attempt_update.dict(exclude_unset=True),
    )

    # Update fields
    (
        session
        .query(Attempt)
        .filter(Attempt.id == db_attempt.id)
        .update(attempt_data.dict())
    )

    session.commit()
    session.refresh(db_attempt)

    return db_attempt


def delete_attempt(
    session: Session,
    db_attempt: Attempt,
):
    session.delete(db_attempt)
    session.commit()
