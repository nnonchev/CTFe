import sqlalchemy as sa
from sqlalchemy.orm import relationship

from CTFe.config.database import Base
from CTFe.models.association_tables import attempt_to_challenge_table


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

    challenges = relationship(
        "Challenge",
        secondary=attempt_to_challenge_table,
        back_populates="attempts",
    )

    def __repr__(self):
        return f"<Attempt { self.id }>"

    def __init__(self, flag, team_id):
        self.flag = flag
        self.team_id = team_id
