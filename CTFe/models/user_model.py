import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.orm import relationship

from CTFe.config.database import Base
from CTFe.models.association_tables import team_player_invite_table
from CTFe.utils import (
    enums,
    pwd_utils,
)


class User(Base):
    __tablename__ = "users"

    id = sa.Column(
        sa.Integer(),
        primary_key=True,
    )
    username = sa.Column(
        sa.String(),
        unique=True,
        nullable=False,
    )
    password = sa.Column(
        sa.String(),
        nullable=False,
    )
    user_type = sa.Column(
        sa.String(),
        nullable=False,
        default=enums.UserType.PLAYER,
    )
    # user_type <PLAYER> can join a team
    team_id = sa.Column(
        sa.Integer(),
        sa.ForeignKey("teams.id"),
    )
    team = relationship(
        "Team",
        back_populates="players",
    )
    team_invites = relationship(
        "Team",
        secondary=team_player_invite_table,
        back_populates="player_invites",
    )
    # user_type <CONTRIBUTOR> can be owner of challenges
    challenges = relationship(
        "Challenge",
        back_populates="owner",
    )

    def __repr__(self):
        return f"<User { self.id }>"

    def __init__(self, username, password):
        self.username = username
        self.password = password


@event.listens_for(User.password, "set", retval=True)
def hash_password(target, value, oldvalue, initiator):
    hashed_password = pwd_utils.hash_password(value)

    return hashed_password
