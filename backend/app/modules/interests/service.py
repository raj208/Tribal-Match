from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.interests.repository import (
    create_interest,
    create_shortlist,
    delete_shortlist,
    get_interest_by_sender_receiver,
    get_shortlist_by_id_for_user,
    get_shortlist_by_user_and_profile,
    list_received_interests_for_user,
    list_sent_interests_for_user,
    list_shortlists_for_user,
)
from app.modules.moderation.repository import is_blocked_between
from app.modules.profiles.models import Profile
from app.modules.users.models import User
from app.shared.enums import InterestStatus, ProfileStatus


def _get_primary_photo_url(profile) -> str | None:
    if not getattr(profile, "photos", None):
        return None

    for photo in profile.photos:
        if photo.is_primary:
            return photo.photo_url

    return profile.photos[0].photo_url


def _get_target_profile_or_404(db: Session, *, profile_id: UUID, current_user: User) -> Profile:
    stmt = select(Profile).where(
        Profile.id == profile_id,
        Profile.profile_status == ProfileStatus.PUBLISHED,
    )
    profile = db.scalar(stmt)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target profile not found",
        )

    if profile.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot interact with your own profile",
        )

    if is_blocked_between(
        db,
        user_a_id=current_user.id,
        user_b_id=profile.user_id,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Interaction unavailable for this profile",
        )

    return profile


def _serialize_shortlist_item(item) -> dict:
    profile = item.profile
    return {
        "id": item.id,
        "profile_id": profile.id,
        "full_name": profile.full_name,
        "age": profile.age,
        "community_or_tribe": profile.community_or_tribe,
        "native_language": profile.native_language,
        "location_city": profile.location_city,
        "occupation": profile.occupation,
        "bio": profile.bio,
        "verification_status": profile.verification_status,
        "primary_photo_url": _get_primary_photo_url(profile),
        "created_at": item.created_at,
    }


def _serialize_interest_item(interest, *, direction: str) -> dict:
    profile = interest.receiver_profile if direction == "sent" else interest.sender_profile

    return {
        "id": interest.id,
        "profile_id": profile.id,
        "full_name": profile.full_name,
        "age": profile.age,
        "community_or_tribe": profile.community_or_tribe,
        "native_language": profile.native_language,
        "location_city": profile.location_city,
        "occupation": profile.occupation,
        "bio": profile.bio,
        "verification_status": profile.verification_status,
        "primary_photo_url": _get_primary_photo_url(profile),
        "status": interest.status,
        "direction": direction,
        "created_at": interest.created_at,
    }


def add_to_shortlist(db: Session, *, current_user: User, profile_id: UUID) -> dict:
    profile = _get_target_profile_or_404(db, profile_id=profile_id, current_user=current_user)

    existing = get_shortlist_by_user_and_profile(
        db,
        user_id=current_user.id,
        profile_id=profile.id,
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already shortlisted",
        )

    item = create_shortlist(
        db,
        {
            "user_id": current_user.id,
            "shortlisted_profile_id": profile.id,
        },
    )

    item.profile = profile
    return _serialize_shortlist_item(item)


def list_my_shortlists(db: Session, *, current_user: User) -> list[dict]:
    items = list_shortlists_for_user(db, user_id=current_user.id)
    return [_serialize_shortlist_item(item) for item in items]


def remove_from_shortlist(db: Session, *, current_user: User, shortlist_id: UUID) -> None:
    item = get_shortlist_by_id_for_user(
        db,
        shortlist_id=shortlist_id,
        user_id=current_user.id,
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shortlist item not found",
        )

    delete_shortlist(db, item)


def send_interest(db: Session, *, current_user: User, receiver_profile_id: UUID) -> dict:
    receiver_profile = _get_target_profile_or_404(
        db,
        profile_id=receiver_profile_id,
        current_user=current_user,
    )

    sender_profile_stmt = select(Profile).where(Profile.user_id == current_user.id)
    sender_profile = db.scalar(sender_profile_stmt)

    if not sender_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Create your own profile before sending interest",
        )

    existing = get_interest_by_sender_receiver(
        db,
        sender_user_id=current_user.id,
        receiver_user_id=receiver_profile.user_id,
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Interest already sent to this profile",
        )

    item = create_interest(
        db,
        {
            "sender_user_id": current_user.id,
            "receiver_user_id": receiver_profile.user_id,
            "sender_profile_id": sender_profile.id,
            "receiver_profile_id": receiver_profile.id,
            "status": InterestStatus.SENT,
        },
    )

    item.receiver_profile = receiver_profile
    return _serialize_interest_item(item, direction="sent")


def list_my_sent_interests(db: Session, *, current_user: User) -> list[dict]:
    items = list_sent_interests_for_user(db, user_id=current_user.id)
    return [_serialize_interest_item(item, direction="sent") for item in items]


def list_my_received_interests(db: Session, *, current_user: User) -> list[dict]:
    items = list_received_interests_for_user(db, user_id=current_user.id)
    return [_serialize_interest_item(item, direction="received") for item in items]