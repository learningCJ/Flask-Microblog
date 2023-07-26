"""changed the article body datatype

Revision ID: 0a53ecbc4dc8
Revises: 667bc7c00490
Create Date: 2023-07-26 08:56:53.516290

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a53ecbc4dc8'
down_revision = '667bc7c00490'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('article', schema=None) as batch_op:
        batch_op.alter_column('body',
               existing_type=sa.VARCHAR(length=14383),
               type_=sa.Text(length=30000),
               existing_nullable=False)


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    with op.batch_alter_table('article', schema=None) as batch_op:
        batch_op.alter_column('body',
               existing_type=sa.Text(length=30000),
               type_=sa.VARCHAR(length=14383),
               existing_nullable=False)

    # ### end Alembic commands ###
