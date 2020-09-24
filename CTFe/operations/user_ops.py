from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import BooleanClauseList

from CTFe.models import User
from CTFe.schemas import user_schemas
from CTFe.utils import pwd_utils


def create_user(
    session: Session,
    user_create: user_schemas.UserCreate,
) -> User:
    
    # TODO Find a better solution
    # Hash password
    user_create.password = pwd_utils.hash_password(user_create.password)

    db_user = User(**user_create.dict())

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


def read_users_by_(
    session: Session,
    conditions: BooleanClauseList,
) -> User:
    """ Query DB for user records based on multiple queries """
    return session.query(User).filter(conditions)


def update_user(
    session: Session,
    db_user: User,
    user_update: Any,
) -> User:
    """ Update user record in DB """

    if user_update.password is not None:
        # TODO Find a better solution
        # Hash password
        user_update.password = pwd_utils.hash_password(user_update.password)

    # Cast to UserUpdate pydantic model
    user_updated = (
        user_schemas.UserUpdate.from_orm(db_user)
    )

    # Update the new fields
    user_data = user_updated.copy(
        update=user_update.dict(exclude_unset=True),
    )

    # Update fields
    (
        session
        .query(User)
        .filter(User.id == db_user.id)
        .update(user_data.dict())
    )

    session.commit()
    session.refresh(db_user)

    return db_user


def delete_user(
    session: Session,
    db_user: User,
):
    session.delete(db_user)
    session.commit()
