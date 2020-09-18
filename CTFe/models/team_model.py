import sqlalchemy as sa
from sqlalchemy.orm import relationship

from CTFe.config.database import Base


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

    def __repr__(self):
        return f"<Team { self.id }>"

    def __init__(self, name):
        self.name = name
