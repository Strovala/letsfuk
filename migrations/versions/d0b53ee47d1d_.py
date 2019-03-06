"""empty message

Revision ID: d0b53ee47d1d
Revises: c9fb0052c00b
Create Date: 2019-03-06 23:27:55.912375

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0b53ee47d1d'
down_revision = 'c9fb0052c00b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'salt')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('salt', sa.VARCHAR(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
