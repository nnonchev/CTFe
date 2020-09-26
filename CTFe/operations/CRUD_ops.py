from typing import Optional

from pydantic import BaseModel as SchemaBase
from sqlalchemy.orm import (
    Session,
    Query,
)
from sqlalchemy.sql.expression import BooleanClauseList

from CTFe.config.database import Base as ModelBase


def create_record(
    session: Session,
    Model: ModelBase,
    schema_create: SchemaBase,
) -> ModelBase:
    """ Create DB record """

    db_model = Model(**schema_create.dict())

    session.add(db_model)
    session.commit()
    session.refresh(db_model)

    return db_model


def query_records(
    session: Session,
    Model: ModelBase,
    conditions: BooleanClauseList,
) -> Query:
    """ Query DB for record/s """

    query = (
        session
        .query(Model)
        .filter(conditions)
    )

    return query


def update_record(
    session: Session,
    db_model: ModelBase,
    schema_update: Optional[SchemaBase] = [],
) -> ModelBase:
    """ Update DB record """

    for field, value in schema_update.dict(exclude_unset=True).items():
        setattr(db_model, field, value)

    session.commit()
    session.refresh(db_model)

    return db_model


def delete_record(
    session: Session,
    db_model: ModelBase,
) -> ModelBase:
    """ Delete DB record """

    session.delete(db_model)
    session.commit()
