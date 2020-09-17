import sqlalchemy as sa
from sqlalchemy.orm import relationship

from CTFe.config.database import Base
from CTFe.utils.enums import UserType


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
        nullable=True,
    )
    user_type = sa.Column(
        sa.Enum(UserType),
        nullable=False,
        server_default=UserType.PLAYER.name,
    )
    team_id = sa.Column(
        sa.Integer(),
        sa.ForeignKey("teams.id"),
    )
    team = relationship(
        "Team",
        back_populates="players",
    )

    def __repr__(self):
        return f"<User { self.id }>"

    def __init__(self, username, password):
        self.username = username
        self.password = password
