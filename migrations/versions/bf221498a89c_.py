"""empty message

Revision ID: bf221498a89c
Revises: 12150291a0a2
Create Date: 2021-06-02 21:55:38.565566

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'bf221498a89c'
down_revision = '12150291a0a2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('artist', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('artist', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('artist', 'city',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('artist', 'state',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('show', 'start_time',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('venue', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('venue', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('venue', 'address',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('venue', 'city',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('venue', 'state',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('venue', 'state',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('venue', 'city',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('venue', 'address',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('venue', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('venue', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('show', 'start_time',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('artist', 'state',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('artist', 'city',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('artist', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('artist', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###