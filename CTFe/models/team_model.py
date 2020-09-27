import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from CTFe.config.database import Base
from CTFe.models.association_tables import team_player_invite_table


class Team(Base):
    __tablename__ = "teams"

    id = sa.Column(
        sa.Integer(),
        primary_key=True,
    )
    name = sa.Column(
        sa.String(),
        unique=True,
        nullable=False,
    )
    players = relationship(
        "User",
        back_populates="team",
    )

    attempts = relationship(
        "Attempt",
        back_populates="team",
        cascade="all, delete-orphan",
    )
    player_invites = relationship(
        "User",
        secondary=team_player_invite_table,
        back_populates="team_invites",
    )

    def __repr__(self):
        return f"<Team { self.id }>"

    def __init__(self, name):
        self.name = name

    @hybrid_property
    def captain(self):
        if len(self.players) > 0:
            return self.players[0]
        return None
