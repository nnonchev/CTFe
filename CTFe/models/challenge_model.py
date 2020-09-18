from datetime import datetime

import sqlalchemy as sa

from CTFe.config.database import Base


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

    def __repr__(self):
        return f"<Challenge { self.id }>"

    def __init__(self, name, description, flag, file_name):
        self.name = name
        self.description = description
        self.flag = flag
        self.file_name = file_name
