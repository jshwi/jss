"""Initial schema

Revision ID: 50587486df14
Revises: 
Create Date: 2021-10-01 23:34:21.390176

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '50587486df14'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('admin', sa.Boolean(), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('confirmed_on', sa.DateTime(), nullable=True),
    sa.Column('about_me', sa.String(length=140), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_confirmed_on'), 'user', ['confirmed_on'], unique=False)
    op.create_index(op.f('ix_user_created'), 'user', ['created'], unique=False)
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('body', sa.String(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_post_created'), 'post', ['created'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_post_created'), table_name='post')
    op.drop_table('post')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_index(op.f('ix_user_created'), table_name='user')
    op.drop_index(op.f('ix_user_confirmed_on'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
