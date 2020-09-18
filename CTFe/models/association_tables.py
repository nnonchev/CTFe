import sqlalchemy as sa

from CTFe.config.database import Base


attempt_to_challenge_table = sa.Table(
    "attempt_to_challenge_table", Base.metadata,
    sa.Column("attempts_id", sa.Integer(), sa.ForeignKey("attempts.id")),
    sa.Column("challenges_id", sa.Integer(), sa.ForeignKey("challenges.id")),
)
