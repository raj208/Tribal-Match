"""create shortlists and interests

Revision ID: 0002_shortlists_interests
Revises: 0001_initial_schema
Create Date: 2026-04-13 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_shortlists_interests"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


interest_status_enum = sa.Enum(
    "sent",
    "accepted",
    "declined",
    name="interest_status_enum",
)


def upgrade() -> None:
    bind = op.get_bind()
    interest_status_enum.create(bind, checkfirst=True)

    op.create_table(
        "shortlists",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("shortlisted_profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", "shortlisted_profile_id", name="uq_shortlists_user_profile"),
    )

    op.create_table(
        "interests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("sender_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("receiver_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("receiver_profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", interest_status_enum, nullable=False, server_default="sent"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("sender_user_id", "receiver_user_id", name="uq_interests_sender_receiver"),
    )


def downgrade() -> None:
    op.drop_table("interests")
    op.drop_table("shortlists")

    bind = op.get_bind()
    interest_status_enum.drop(bind, checkfirst=True)
