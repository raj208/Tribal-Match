"""initial schema

Revision ID: 0001_initial_schema
Revises: None
Create Date: 2026-04-11 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


profile_status_enum = postgresql.ENUM(
    "draft",
    "published",
    "hidden",
    "deactivated",
    "deleted",
    name="profile_status_enum",
    create_type=False,
)

verification_status_enum = postgresql.ENUM(
    "not_started",
    "uploaded",
    "under_review",
    "approved",
    "rejected",
    name="verification_status_enum",
    create_type=False,
)

video_verification_status_enum = postgresql.ENUM(
    "not_started",
    "uploaded",
    "under_review",
    "approved",
    "rejected",
    name="video_verification_status_enum",
    create_type=False,
)

moderation_status_enum = postgresql.ENUM(
    "clean",
    "flagged",
    "under_review",
    "action_taken",
    name="moderation_status_enum",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    profile_status_enum.create(bind, checkfirst=True)
    verification_status_enum.create(bind, checkfirst=True)
    video_verification_status_enum.create(bind, checkfirst=True)
    moderation_status_enum.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("auth_provider", sa.String(length=32), nullable=False, server_default="supabase"),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="user"),
        sa.Column("account_status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("phone_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_phone", "users", ["phone"], unique=True)

    op.create_table(
        "profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("gender", sa.String(length=32), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("community_or_tribe", sa.String(length=120), nullable=True),
        sa.Column("subgroup_or_clan", sa.String(length=120), nullable=True),
        sa.Column("native_language", sa.String(length=80), nullable=True),
        sa.Column("other_languages", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("location_city", sa.String(length=120), nullable=True),
        sa.Column("location_state", sa.String(length=120), nullable=True),
        sa.Column("location_country", sa.String(length=120), nullable=True),
        sa.Column("occupation", sa.String(length=120), nullable=True),
        sa.Column("education", sa.String(length=120), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("profile_visibility", sa.String(length=32), nullable=False, server_default="public"),
        sa.Column("profile_status", profile_status_enum, nullable=False, server_default="draft"),
        sa.Column("verification_status", verification_status_enum, nullable=False, server_default="not_started"),
        sa.Column("completion_percentage", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", name="uq_profiles_user_id"),
    )

    op.create_table(
        "profile_photos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("photo_url", sa.String(length=500), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("moderation_status", moderation_status_enum, nullable=False, server_default="clean"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "intro_videos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("video_url", sa.String(length=500), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("upload_status", sa.String(length=32), nullable=False, server_default="uploaded"),
        sa.Column("verification_status", video_verification_status_enum, nullable=False, server_default="uploaded"),
        sa.Column("moderation_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("profile_id", name="uq_intro_videos_profile_id"),
    )

    op.create_table(
        "preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("preferred_min_age", sa.Integer(), nullable=True),
        sa.Column("preferred_max_age", sa.Integer(), nullable=True),
        sa.Column("preferred_locations", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("preferred_communities", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("preferred_languages", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", name="uq_preferences_user_id"),
        sa.UniqueConstraint("profile_id", name="uq_preferences_profile_id"),
    )


def downgrade() -> None:
    op.drop_table("preferences")
    op.drop_table("intro_videos")
    op.drop_table("profile_photos")
    op.drop_table("profiles")
    op.drop_index("ix_users_phone", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    bind = op.get_bind()
    moderation_status_enum.drop(bind, checkfirst=True)
    video_verification_status_enum.drop(bind, checkfirst=True)
    verification_status_enum.drop(bind, checkfirst=True)
    profile_status_enum.drop(bind, checkfirst=True)
