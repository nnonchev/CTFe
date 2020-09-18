from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from CTFe.config.database import Base
from CTFe.models.association_tables import attempt_to_challenge_table


class Challenge(Base):
    __tablename__ = "challenges"

    id = sa.Column(
        sa.Integer(),
        primary_key=True,
    )
    name = sa.Column(
        sa.String(),
        unique=True,
        nullable=False,
    )
    description = sa.Column(
        sa.String(),
        nullable=True,
    )
    flag = sa.Column(
        sa.String(),
        nullable=False,
    )
    file_name = sa.Column(
        sa.String(),
        nullable=True,
    )
    created_at = sa.Column(
        sa.DateTime(),
        nullable=False,
        default=datetime.utcnow,
    )

    attempts = relationship(
        "Attempt",
        secondary=attempt_to_challenge_table,
        back_populates="challenges"
    )

    def __repr__(self):
        return f"<Challenge { self.id }>"

    def __init__(self, name, description, flag, file_name):
        self.name = name
        self.description = description
        self.flag = flag
        self.file_name = file_name
