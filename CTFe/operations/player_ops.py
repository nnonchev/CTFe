from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import BooleanClauseList

from CTFe.models import User
from CTFe.utils import enums


def read_players_by_(
    session: Session,
    conditions: BooleanClauseList,
) -> User:
    """ Query DB for user records based on multiple queries """
    conditions = and_(
        User.user_type == enums.UserType.PLAYER,
        conditions,
    )
    return session.query(User).filter(conditions)
