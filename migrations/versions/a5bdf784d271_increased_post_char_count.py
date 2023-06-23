"""Increased Post char count

Revision ID: a5bdf784d271
Revises: b3bdf82f4ecd
Create Date: 2023-06-16 17:28:25.619935

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a5bdf784d271'
down_revision = 'b3bdf82f4ecd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.alter_column('body',
               existing_type=sa.VARCHAR(length=150),
               type_=sa.String(length=1500),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.alter_column('body',
               existing_type=sa.String(length=1500),
               type_=sa.VARCHAR(length=150),
               existing_nullable=False)

    # ### end Alembic commands ###