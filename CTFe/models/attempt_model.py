import sqlalchemy as sa
from sqlalchemy.orm import relationship

from CTFe.config.database import Base


class Attempt(Base):
    __tablename__ = "attempts"

    id = sa.Column(
        sa.Integer(),
        primary_key=True,
    )
    flag = sa.Column(
        sa.String(),
        nullable=False,
    )
    team_id = sa.Column(
        sa.Integer(),
        sa.ForeignKey("teams.id"),
    )
    team = relationship(
        "Team",
        back_populates="attempts",
    )
    challenge_id = sa.Column(
        sa.Integer(),
        sa.ForeignKey("challenges.id"),
    )
    challenge = relationship(
        "Challenge",
        back_populates="attempts",
    )

    def __repr__(self):
        return f"<Attempt { self.id }>"

    def __init__(self, flag, team_id, challenge_id):
        self.flag = flag
        self.team_id = team_id
        self.challenge_id = challenge_id
