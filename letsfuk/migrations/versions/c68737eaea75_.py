"""empty message

Revision ID: c68737eaea75
Revises: 4eef048c883f
Create Date: 2019-03-21 16:00:06.470390

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c68737eaea75'
down_revision = '4eef048c883f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sessions', sa.Column('expires_at', sa.Date(), nullable=False))
    op.drop_column('sessions', 'created_at')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sessions', sa.Column('created_at', sa.DATE(), autoincrement=False, nullable=False))
    op.drop_column('sessions', 'expires_at')
    # ### end Alembic commands ###
