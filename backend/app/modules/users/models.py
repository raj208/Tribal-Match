# ORM models for the users module will be added in later steps.
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)
    auth_provider: Mapped[str] = mapped_column(String(32), default="supabase", nullable=False)
    role: Mapped[str] = mapped_column(String(32), default="user", nullable=False)
    account_status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    profile: Mapped["Profile | None"] = relationship(back_populates="user", uselist=False)
    preferences: Mapped["Preference | None"] = relationship(back_populates="user", uselist=False)
    photos: Mapped[list["ProfilePhoto"]] = relationship(back_populates="user")
    intro_videos: Mapped[list["IntroVideo"]] = relationship(back_populates="user")