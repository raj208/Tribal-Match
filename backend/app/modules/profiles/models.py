# ORM models for the profiles module will be added in later steps.
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.shared.enums import ProfileStatus, VerificationStatus, enum_values


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(32), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    community_or_tribe: Mapped[str | None] = mapped_column(String(120), nullable=True)
    subgroup_or_clan: Mapped[str | None] = mapped_column(String(120), nullable=True)
    native_language: Mapped[str | None] = mapped_column(String(80), nullable=True)
    other_languages: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    location_city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    location_state: Mapped[str | None] = mapped_column(String(120), nullable=True)
    location_country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    occupation: Mapped[str | None] = mapped_column(String(120), nullable=True)
    education: Mapped[str | None] = mapped_column(String(120), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    profile_visibility: Mapped[str] = mapped_column(String(32), default="public", nullable=False)
    profile_status: Mapped[ProfileStatus] = mapped_column(
        Enum(ProfileStatus, name="profile_status_enum", values_callable=enum_values, validate_strings=True),
        default=ProfileStatus.DRAFT,
        nullable=False,
    )
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(
            VerificationStatus,
            name="verification_status_enum",
            values_callable=enum_values,
            validate_strings=True,
        ),
        default=VerificationStatus.NOT_STARTED,
        nullable=False,
    )
    completion_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="profile")
    photos: Mapped[list["ProfilePhoto"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )
    intro_video: Mapped["IntroVideo | None"] = relationship(
        back_populates="profile", uselist=False, cascade="all, delete-orphan"
    )
    preferences: Mapped["Preference | None"] = relationship(
        back_populates="profile", uselist=False, cascade="all, delete-orphan"
    )


class Preference(Base):
    __tablename__ = "preferences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    preferred_min_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    preferred_max_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    preferred_locations: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    preferred_communities: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    preferred_languages: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="preferences")
    profile: Mapped[Profile] = relationship(back_populates="preferences")
