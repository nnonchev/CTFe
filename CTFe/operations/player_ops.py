from sqlalchemy import and_
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import BooleanClauseList

from CTFe.models import User
from CTFe.operations import user_ops
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

    return user_ops.read_users_by_(session, conditions)


def quit_team(
    db_user: User,
    session: Session,
) -> User:
    """ Remove current team from player """
    team = db_user.team
    

    db_user.team = None

    session.add(db_user)
    session.commit()

    session.refresh(db_user)

    return db_user
