"""initial persistence schema

Revision ID: 20260910_01
Revises:
Create Date: 2026-09-10
"""
from alembic import op

from app.database import Base
import app.models  # noqa: F401 - register metadata before create_all/drop_all

revision = "20260910_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
