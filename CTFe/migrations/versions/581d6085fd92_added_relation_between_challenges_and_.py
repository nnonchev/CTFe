"""Added relation between challenges and contributors

Revision ID: 581d6085fd92
Revises: 8b5354f3bc6a
Create Date: 2020-09-24 10:45:26.340162

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '581d6085fd92'
down_revision = '8b5354f3bc6a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('challenges', sa.Column('owner_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'challenges', 'users', ['owner_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'challenges', type_='foreignkey')
    op.drop_column('challenges', 'owner_id')
    # ### end Alembic commands ###
