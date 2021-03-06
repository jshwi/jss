"""Adds `Usernames` model

Revision ID: 61a01b56cb45
Revises: ee3c6c0702a6
Create Date: 2021-10-11 00:13:34.116984

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61a01b56cb45'
down_revision = 'ee3c6c0702a6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('usernames',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_usernames_username'), 'usernames', ['username'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_usernames_username'), table_name='usernames')
    op.drop_table('usernames')
    # ### end Alembic commands ###
