import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from CTFe.config.database import Base
from CTFe.utils import enums


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
        sa.Enum(enums.UserType),
        nullable=False,
        server_default=enums.UserType.PLAYER.name,
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
