import sqlalchemy as sa

from CTFe.config.database import Base


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