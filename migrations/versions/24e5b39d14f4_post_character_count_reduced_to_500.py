"""post character count reduced to 500

Revision ID: 24e5b39d14f4
Revises: a5bdf784d271
Create Date: 2023-06-20 15:10:29.480236

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24e5b39d14f4'
down_revision = 'a5bdf784d271'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.alter_column('body',
               existing_type=sa.VARCHAR(length=1500),
               type_=sa.String(length=500),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.alter_column('body',
               existing_type=sa.String(length=500),
               type_=sa.VARCHAR(length=1500),
               existing_nullable=False)

    # ### end Alembic commands ###
