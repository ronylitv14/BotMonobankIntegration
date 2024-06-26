"""Added flag  for Chat model

Revision ID: c76350e284ff
Revises: 8b73cc297802
Create Date: 2024-01-22 10:43:01.131006

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c76350e284ff'
down_revision = '8b73cc297802'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chats', sa.Column('active', sa.Boolean(), server_default=sa.text('true'), nullable=False))

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('chats', 'active')
    # ### end Alembic commands ###
