"""add supabase user id to users

Revision ID: 0004_add_supa_uid
Revises: 0003_create_blocks_and_reports
Create Date: 2026-04-15 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_add_supa_uid"
down_revision = "0003_create_blocks_and_reports"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("supabase_user_id", sa.String(length=64), nullable=True))
    op.create_index("ix_users_supabase_user_id", "users", ["supabase_user_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_supabase_user_id", table_name="users")
    op.drop_column("users", "supabase_user_id")
