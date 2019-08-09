"""Added avatar key to user model

Revision ID: 7fc62c6eafb3
Revises: 73f6a2d5de8c
Create Date: 2019-08-09 18:36:02.184226

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7fc62c6eafb3'
down_revision = '73f6a2d5de8c'
branch_labels = None
depends_on = None


from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('users', sa.Column('avatar_key', sa.String, nullable=True, unique=True))

def downgrade():
    op.drop_column('users', 'avatar_key')
