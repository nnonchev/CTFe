from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import (
    and_,
    BooleanClauseList,
)

from CTFe.models import User
from CTFe.schemas import user_schemas


def create_user(
    session: Session,
    user_create: user_schemas.UserCreate,
) -> User:
    db_user = User(**user_create.dict())

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


def read_user_by_(
    session: Session,
    conditions: BooleanClauseList,
) -> User:
    """ Query DB for a user based on multiple queries """
    return session.query(User).filter(conditions).first()
