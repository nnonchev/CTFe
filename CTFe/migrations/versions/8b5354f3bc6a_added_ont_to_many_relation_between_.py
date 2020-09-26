"""Added one to many relation between attempts and challenges

Revision ID: 8b5354f3bc6a
Revises: ab3e2713831b
Create Date: 2020-09-18 22:16:18.300879

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b5354f3bc6a'
down_revision = 'ab3e2713831b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('attempts', sa.Column('challenge_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'attempts', 'challenges', ['challenge_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'attempts', type_='foreignkey')
    op.drop_column('attempts', 'challenge_id')
    # ### end Alembic commands ###
