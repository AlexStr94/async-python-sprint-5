"""01_initial-db

Revision ID: 7215d1c0134c
Revises: 
Create Date: 2023-06-08 14:48:26.030450

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '7215d1c0134c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('hashed_password', sa.String(length=100), nullable=False),
    sa.Column('uuid', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username'),
    sa.UniqueConstraint('uuid')
    )
    op.create_table('files',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('path', sa.String(length=300), nullable=False),
    sa.Column('size', sa.Integer(), nullable=False),
    sa.Column('is_downloadable', sa.Boolean(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('uuid', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('path'),
    sa.UniqueConstraint('uuid')
    )
    op.create_index(op.f('ix_files_created_at'), 'files', ['created_at'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_files_created_at'), table_name='files')
    op.drop_table('files')
    op.drop_table('users')
    # ### end Alembic commands ###
