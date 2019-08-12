"""Added image_key to private and station chat

Revision ID: 9f6c813acf7d
Revises: 7fc62c6eafb3
Create Date: 2019-08-12 20:22:30.309172

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f6c813acf7d'
down_revision = '7fc62c6eafb3'
branch_labels = None
depends_on = None


from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('private_chats', sa.Column('image_key', sa.String, nullable=True))
    op.add_column('station_chats', sa.Column('image_key', sa.String, nullable=True))
    op.alter_column('private_chats', 'text', nullable=True)
    op.alter_column('station_chats', 'text', nullable=True)

def downgrade():
    op.drop_column('station_chats', 'image_key')
    op.drop_column('private_chats', 'image_key')
    op.alter_column('private_chats', 'text', nullable=False)
    op.alter_column('station_chats', 'text', nullable=False)
