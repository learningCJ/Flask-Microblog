"""removed isTempAccount

Revision ID: fe015a0ee72d
Revises: 35778f592e51
Create Date: 2023-07-20 11:26:54.769161

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe015a0ee72d'
down_revision = '35778f592e51'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('isTempAccount')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('isTempAccount', sa.BOOLEAN(), nullable=True))

    # ### end Alembic commands ###
