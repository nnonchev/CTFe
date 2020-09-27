import sqlalchemy as sa

from CTFe.config.database import Base


team_player_invite_table = sa.Table(
    "team_player_invite_table", Base.metadata,
    sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id")),
    sa.Column('user_id', sa.Integer(), sa.ForeignKey("users.id")),
)
