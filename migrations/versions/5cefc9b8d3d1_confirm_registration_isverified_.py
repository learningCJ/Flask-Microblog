"""confirm registration isVerified NonOptional

Revision ID: 5cefc9b8d3d1
Revises: d4423ae9eb93
Create Date: 2023-05-24 11:25:46.842737

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5cefc9b8d3d1'
down_revision = 'd4423ae9eb93'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('isVerified',
               existing_type=sa.BOOLEAN(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('isVerified',
               existing_type=sa.BOOLEAN(),
               nullable=True)

    # ### end Alembic commands ###
