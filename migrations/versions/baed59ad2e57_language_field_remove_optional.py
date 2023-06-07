"""language field remove optional

Revision ID: baed59ad2e57
Revises: fd5b0b855e5a
Create Date: 2023-04-26 12:59:32.182799

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'baed59ad2e57'
down_revision = 'fd5b0b855e5a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('_alembic_tmp_post')
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.alter_column('language',
               existing_type=sa.VARCHAR(length=10),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.alter_column('language',
               existing_type=sa.VARCHAR(length=10),
               nullable=True)

    op.create_table('_alembic_tmp_post',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('body', sa.VARCHAR(length=140), nullable=False),
    sa.Column('timestamp', sa.DATETIME(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('language', sa.VARCHAR(length=10), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
