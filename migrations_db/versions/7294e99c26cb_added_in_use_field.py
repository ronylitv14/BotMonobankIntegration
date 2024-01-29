"""Added in_use field

Revision ID: 7294e99c26cb
Revises: 6416ea68047d
Create Date: 2024-01-24 19:26:02.258890

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7294e99c26cb'
down_revision = '6416ea68047d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chats', sa.Column('in_use', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('chats', 'in_use')
    # ### end Alembic commands ###
