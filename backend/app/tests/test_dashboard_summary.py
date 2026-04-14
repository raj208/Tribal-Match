from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.interests.models import Interest, Shortlist
from app.modules.media.models import IntroVideo, ProfilePhoto
from app.modules.profiles.models import Profile
from app.modules.users.models import User
from app.shared.enums import InterestStatus, ProfileStatus, VerificationStatus

DASHBOARD_SUMMARY_PATH = f"{settings.api_v1_prefix}/dashboard/summary"


def _auth_headers(email: str) -> dict[str, str]:
    return {"X-User-Email": email}


def _create_user(db: Session, email: str) -> User:
    user = User(email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _create_profile(
    db: Session,
    *,
    user: User,
    full_name: str,
    profile_status: ProfileStatus = ProfileStatus.DRAFT,
    verification_status: VerificationStatus = VerificationStatus.NOT_STARTED,
    completion_percentage: int = 0,
) -> Profile:
    profile = Profile(
        user_id=user.id,
        full_name=full_name,
        profile_status=profile_status,
        verification_status=verification_status,
        completion_percentage=completion_percentage,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def _create_photo(db: Session, *, user: User, profile: Profile, photo_url: str, sort_order: int = 0) -> ProfilePhoto:
    photo = ProfilePhoto(
        user_id=user.id,
        profile_id=profile.id,
        photo_url=photo_url,
        sort_order=sort_order,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def _create_intro_video(db: Session, *, user: User, profile: Profile, video_url: str) -> IntroVideo:
    intro_video = IntroVideo(
        user_id=user.id,
        profile_id=profile.id,
        video_url=video_url,
    )
    db.add(intro_video)
    db.commit()
    db.refresh(intro_video)
    return intro_video


def _create_shortlist(db: Session, *, user: User, shortlisted_profile: Profile) -> Shortlist:
    shortlist = Shortlist(
        user_id=user.id,
        shortlisted_profile_id=shortlisted_profile.id,
    )
    db.add(shortlist)
    db.commit()
    db.refresh(shortlist)
    return shortlist


def _create_interest(
    db: Session,
    *,
    sender_user: User,
    receiver_user: User,
    sender_profile: Profile,
    receiver_profile: Profile,
    status: InterestStatus = InterestStatus.SENT,
) -> Interest:
    interest = Interest(
        sender_user_id=sender_user.id,
        receiver_user_id=receiver_user.id,
        sender_profile_id=sender_profile.id,
        receiver_profile_id=receiver_profile.id,
        status=status,
    )
    db.add(interest)
    db.commit()
    db.refresh(interest)
    return interest


def test_dashboard_summary_requires_auth(client) -> None:
    response = client.get(DASHBOARD_SUMMARY_PATH)

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_dashboard_summary_returns_defaults_when_profile_is_missing(client) -> None:
    response = client.get(
        DASHBOARD_SUMMARY_PATH,
        headers=_auth_headers("no-profile@example.com"),
    )

    assert response.status_code == 200
    assert response.json() == {
        "profile_exists": False,
        "profile_status": None,
        "completion_percentage": 0,
        "verification_status": "not_started",
        "photo_count": 0,
        "has_intro_video": False,
        "shortlist_count": 0,
        "sent_interests_count": 0,
        "received_interests_count": 0,
    }


def test_dashboard_summary_returns_zero_counts_for_profile_without_media_or_interactions(client, db_session: Session) -> None:
    user = _create_user(db_session, "profile-only@example.com")
    _create_profile(
        db_session,
        user=user,
        full_name="Profile Only",
        profile_status=ProfileStatus.DRAFT,
        verification_status=VerificationStatus.UPLOADED,
        completion_percentage=35,
    )

    response = client.get(
        DASHBOARD_SUMMARY_PATH,
        headers=_auth_headers(user.email),
    )

    assert response.status_code == 200
    assert response.json() == {
        "profile_exists": True,
        "profile_status": "draft",
        "completion_percentage": 35,
        "verification_status": "uploaded",
        "photo_count": 0,
        "has_intro_video": False,
        "shortlist_count": 0,
        "sent_interests_count": 0,
        "received_interests_count": 0,
    }


def test_dashboard_summary_returns_aggregated_counts_for_existing_data(client, db_session: Session) -> None:
    current_user = _create_user(db_session, "current@example.com")
    current_profile = _create_profile(
        db_session,
        user=current_user,
        full_name="Current User",
        profile_status=ProfileStatus.PUBLISHED,
        verification_status=VerificationStatus.APPROVED,
        completion_percentage=90,
    )

    target_user_one = _create_user(db_session, "target-one@example.com")
    target_profile_one = _create_profile(
        db_session,
        user=target_user_one,
        full_name="Target One",
        profile_status=ProfileStatus.PUBLISHED,
        completion_percentage=80,
    )

    target_user_two = _create_user(db_session, "target-two@example.com")
    target_profile_two = _create_profile(
        db_session,
        user=target_user_two,
        full_name="Target Two",
        profile_status=ProfileStatus.PUBLISHED,
        completion_percentage=75,
    )

    sender_user = _create_user(db_session, "sender@example.com")
    sender_profile = _create_profile(
        db_session,
        user=sender_user,
        full_name="Incoming Sender",
        profile_status=ProfileStatus.PUBLISHED,
        completion_percentage=88,
    )

    unrelated_user = _create_user(db_session, "unrelated@example.com")
    unrelated_profile = _create_profile(
        db_session,
        user=unrelated_user,
        full_name="Unrelated User",
        profile_status=ProfileStatus.PUBLISHED,
        completion_percentage=50,
    )

    _create_photo(db_session, user=current_user, profile=current_profile, photo_url="https://example.com/photo-1.jpg")
    _create_photo(
        db_session,
        user=current_user,
        profile=current_profile,
        photo_url="https://example.com/photo-2.jpg",
        sort_order=1,
    )
    _create_photo(db_session, user=target_user_one, profile=target_profile_one, photo_url="https://example.com/other.jpg")
    _create_intro_video(db_session, user=current_user, profile=current_profile, video_url="https://example.com/video.mp4")
    _create_shortlist(db_session, user=current_user, shortlisted_profile=target_profile_one)
    _create_shortlist(db_session, user=current_user, shortlisted_profile=target_profile_two)
    _create_shortlist(db_session, user=target_user_one, shortlisted_profile=current_profile)
    _create_interest(
        db_session,
        sender_user=current_user,
        receiver_user=target_user_one,
        sender_profile=current_profile,
        receiver_profile=target_profile_one,
    )
    _create_interest(
        db_session,
        sender_user=current_user,
        receiver_user=target_user_two,
        sender_profile=current_profile,
        receiver_profile=target_profile_two,
    )
    _create_interest(
        db_session,
        sender_user=sender_user,
        receiver_user=current_user,
        sender_profile=sender_profile,
        receiver_profile=current_profile,
    )
    _create_interest(
        db_session,
        sender_user=target_user_one,
        receiver_user=unrelated_user,
        sender_profile=target_profile_one,
        receiver_profile=unrelated_profile,
    )

    response = client.get(
        DASHBOARD_SUMMARY_PATH,
        headers=_auth_headers(current_user.email),
    )

    assert response.status_code == 200
    assert response.json() == {
        "profile_exists": True,
        "profile_status": "published",
        "completion_percentage": 90,
        "verification_status": "approved",
        "photo_count": 2,
        "has_intro_video": True,
        "shortlist_count": 2,
        "sent_interests_count": 2,
        "received_interests_count": 1,
    }


def test_dashboard_summary_handles_missing_optional_related_records(client, db_session: Session) -> None:
    current_user = _create_user(db_session, "partial@example.com")
    current_profile = _create_profile(
        db_session,
        user=current_user,
        full_name="Partial Data User",
        profile_status=ProfileStatus.DRAFT,
        verification_status=VerificationStatus.NOT_STARTED,
        completion_percentage=20,
    )

    sender_user = _create_user(db_session, "partial-sender@example.com")
    sender_profile = _create_profile(
        db_session,
        user=sender_user,
        full_name="Partial Sender",
        profile_status=ProfileStatus.PUBLISHED,
        completion_percentage=60,
    )

    _create_photo(
        db_session,
        user=current_user,
        profile=current_profile,
        photo_url=f"https://example.com/{uuid4()}.jpg",
    )
    _create_interest(
        db_session,
        sender_user=sender_user,
        receiver_user=current_user,
        sender_profile=sender_profile,
        receiver_profile=current_profile,
    )

    response = client.get(
        DASHBOARD_SUMMARY_PATH,
        headers=_auth_headers(current_user.email),
    )

    assert response.status_code == 200
    assert response.json() == {
        "profile_exists": True,
        "profile_status": "draft",
        "completion_percentage": 20,
        "verification_status": "not_started",
        "photo_count": 1,
        "has_intro_video": False,
        "shortlist_count": 0,
        "sent_interests_count": 0,
        "received_interests_count": 1,
    }
