from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import (
    and_,
    BooleanClauseList,
)

from CTFe.models import User


def read_user_by_(
    session: Session,
    conditions: BooleanClauseList,
) -> User:
    """ Query DB for a user based on multiple queries """
    return session.query(User).filter(conditions).first()
