"""init

Revision ID: 3eb251dea0b5
Revises: b0f6ac254352
Create Date: 2024-03-25 05:09:26.390893

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3eb251dea0b5'
down_revision = 'b0f6ac254352'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('sending_25_march', sa.TIMESTAMP(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'sending_25_march')
    # ### end Alembic commands ###