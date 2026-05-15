"""add profile social links

Revision ID: 0006_add_profile_social_links
Revises: 0005_add_media_storage_metadata
Create Date: 2026-05-15 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0006_add_profile_social_links"
down_revision = "0005_add_media_storage_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("profiles") as batch_op:
        batch_op.add_column(sa.Column("instagram_url", sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column("facebook_url", sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column("linkedin_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("profiles") as batch_op:
        batch_op.drop_column("linkedin_url")
        batch_op.drop_column("facebook_url")
        batch_op.drop_column("instagram_url")
