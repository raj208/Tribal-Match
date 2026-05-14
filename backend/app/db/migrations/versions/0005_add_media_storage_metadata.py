"""add media storage metadata

Revision ID: 0005_add_media_storage_metadata
Revises: 0004_add_supa_uid
Create Date: 2026-04-21 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0005_add_media_storage_metadata"
down_revision = "0004_add_supa_uid"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("profile_photos") as batch_op:
        batch_op.add_column(sa.Column("provider", sa.String(length=32), nullable=False, server_default="local"))
        batch_op.add_column(sa.Column("bucket", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("object_key", sa.String(length=1024), nullable=True))
        batch_op.add_column(sa.Column("content_type", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("size_bytes", sa.BigInteger(), nullable=True))

    with op.batch_alter_table("intro_videos") as batch_op:
        batch_op.add_column(sa.Column("provider", sa.String(length=32), nullable=False, server_default="local"))
        batch_op.add_column(sa.Column("bucket", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("object_key", sa.String(length=1024), nullable=True))
        batch_op.add_column(sa.Column("content_type", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("size_bytes", sa.BigInteger(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("intro_videos") as batch_op:
        batch_op.drop_column("size_bytes")
        batch_op.drop_column("content_type")
        batch_op.drop_column("object_key")
        batch_op.drop_column("bucket")
        batch_op.drop_column("provider")

    with op.batch_alter_table("profile_photos") as batch_op:
        batch_op.drop_column("size_bytes")
        batch_op.drop_column("content_type")
        batch_op.drop_column("object_key")
        batch_op.drop_column("bucket")
        batch_op.drop_column("provider")
