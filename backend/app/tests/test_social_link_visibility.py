import pytest
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.interests.models import Interest
from app.modules.moderation.models import Block
from app.modules.profiles.models import Profile
from app.modules.users.models import User
from app.shared.enums import InterestStatus, ProfileStatus

BROWSE_PATH = f"{settings.api_v1_prefix}/profiles"
PROFILE_DETAIL_PATH = f"{settings.api_v1_prefix}/profiles/{{profile_id}}"


def _auth_headers(email: str) -> dict[str, str]:
    return {"Authorization": f"Bearer test-token:{email}"}


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
    profile_status: ProfileStatus = ProfileStatus.PUBLISHED,
    instagram_url: str | None = "https://instagram.com/social.user",
    facebook_url: str | None = "https://facebook.com/social.user",
    linkedin_url: str | None = "https://linkedin.com/in/social-user",
) -> Profile:
    profile = Profile(
        user_id=user.id,
        full_name=full_name,
        profile_status=profile_status,
        instagram_url=instagram_url,
        facebook_url=facebook_url,
        linkedin_url=linkedin_url,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


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


def _create_block(db: Session, *, blocker_user: User, blocked_user: User) -> Block:
    block = Block(
        blocker_user_id=blocker_user.id,
        blocked_user_id=blocked_user.id,
    )
    db.add(block)
    db.commit()
    db.refresh(block)
    return block


def test_browse_cards_do_not_expose_social_links(client, db_session: Session) -> None:
    viewer = _create_user(db_session, "browse-viewer@example.com")
    target_user = _create_user(db_session, "browse-target@example.com")
    target_profile = _create_profile(db_session, user=target_user, full_name="Browse Target")

    response = client.get(BROWSE_PATH, headers=_auth_headers(viewer.email))

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == str(target_profile.id)
    assert "instagram_url" not in body["items"][0]
    assert "facebook_url" not in body["items"][0]
    assert "linkedin_url" not in body["items"][0]


def test_profile_detail_hides_social_links_without_interest(client, db_session: Session) -> None:
    viewer = _create_user(db_session, "no-interest-viewer@example.com")
    target_user = _create_user(db_session, "no-interest-target@example.com")
    target_profile = _create_profile(db_session, user=target_user, full_name="No Interest Target")

    response = client.get(
        PROFILE_DETAIL_PATH.format(profile_id=target_profile.id),
        headers=_auth_headers(viewer.email),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["instagram_url"] is None
    assert body["facebook_url"] is None
    assert body["linkedin_url"] is None


@pytest.mark.parametrize("interest_status", [InterestStatus.SENT, InterestStatus.DECLINED])
def test_profile_detail_hides_social_links_until_interest_is_accepted(
    client,
    db_session: Session,
    interest_status: InterestStatus,
) -> None:
    sender = _create_user(db_session, f"{interest_status.value}-sender@example.com")
    receiver = _create_user(db_session, f"{interest_status.value}-receiver@example.com")
    sender_profile = _create_profile(db_session, user=sender, full_name="Pending Sender")
    receiver_profile = _create_profile(db_session, user=receiver, full_name="Pending Receiver")
    _create_interest(
        db_session,
        sender_user=sender,
        receiver_user=receiver,
        sender_profile=sender_profile,
        receiver_profile=receiver_profile,
        status=interest_status,
    )

    response = client.get(
        PROFILE_DETAIL_PATH.format(profile_id=receiver_profile.id),
        headers=_auth_headers(sender.email),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["instagram_url"] is None
    assert body["facebook_url"] is None
    assert body["linkedin_url"] is None


def test_profile_detail_shows_social_links_to_both_users_after_accepted_interest(
    client,
    db_session: Session,
) -> None:
    sender = _create_user(db_session, "accepted-sender@example.com")
    receiver = _create_user(db_session, "accepted-receiver@example.com")
    sender_profile = _create_profile(
        db_session,
        user=sender,
        full_name="Accepted Sender",
        instagram_url="https://instagram.com/accepted.sender",
        facebook_url="https://facebook.com/accepted.sender",
        linkedin_url="https://linkedin.com/in/accepted-sender",
    )
    receiver_profile = _create_profile(
        db_session,
        user=receiver,
        full_name="Accepted Receiver",
        instagram_url="https://instagram.com/accepted.receiver",
        facebook_url="https://facebook.com/accepted.receiver",
        linkedin_url="https://linkedin.com/in/accepted-receiver",
    )
    _create_interest(
        db_session,
        sender_user=sender,
        receiver_user=receiver,
        sender_profile=sender_profile,
        receiver_profile=receiver_profile,
        status=InterestStatus.ACCEPTED,
    )

    sender_view_response = client.get(
        PROFILE_DETAIL_PATH.format(profile_id=receiver_profile.id),
        headers=_auth_headers(sender.email),
    )
    receiver_view_response = client.get(
        PROFILE_DETAIL_PATH.format(profile_id=sender_profile.id),
        headers=_auth_headers(receiver.email),
    )

    assert sender_view_response.status_code == 200
    assert sender_view_response.json()["instagram_url"] == "https://instagram.com/accepted.receiver"
    assert sender_view_response.json()["facebook_url"] == "https://facebook.com/accepted.receiver"
    assert sender_view_response.json()["linkedin_url"] == "https://linkedin.com/in/accepted-receiver"

    assert receiver_view_response.status_code == 200
    assert receiver_view_response.json()["instagram_url"] == "https://instagram.com/accepted.sender"
    assert receiver_view_response.json()["facebook_url"] == "https://facebook.com/accepted.sender"
    assert receiver_view_response.json()["linkedin_url"] == "https://linkedin.com/in/accepted-sender"


def test_profile_detail_hides_blocked_profile_even_after_accepted_interest(
    client,
    db_session: Session,
) -> None:
    sender = _create_user(db_session, "blocked-sender@example.com")
    receiver = _create_user(db_session, "blocked-receiver@example.com")
    sender_profile = _create_profile(db_session, user=sender, full_name="Blocked Sender")
    receiver_profile = _create_profile(db_session, user=receiver, full_name="Blocked Receiver")
    _create_interest(
        db_session,
        sender_user=sender,
        receiver_user=receiver,
        sender_profile=sender_profile,
        receiver_profile=receiver_profile,
        status=InterestStatus.ACCEPTED,
    )
    _create_block(db_session, blocker_user=receiver, blocked_user=sender)

    response = client.get(
        PROFILE_DETAIL_PATH.format(profile_id=receiver_profile.id),
        headers=_auth_headers(sender.email),
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Profile not found"}


def test_owner_can_view_own_social_links_on_profile_detail(client, db_session: Session) -> None:
    owner = _create_user(db_session, "owner-detail@example.com")
    owner_profile = _create_profile(
        db_session,
        user=owner,
        full_name="Owner Detail",
        profile_status=ProfileStatus.DRAFT,
        instagram_url="https://instagram.com/owner.detail",
    )

    response = client.get(
        PROFILE_DETAIL_PATH.format(profile_id=owner_profile.id),
        headers=_auth_headers(owner.email),
    )

    assert response.status_code == 200
    assert response.json()["instagram_url"] == "https://instagram.com/owner.detail"


def test_admin_can_view_social_links_for_hidden_profile(
    client,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "admin_email_allowlist", ["admin@example.com"])
    target_user = _create_user(db_session, "admin-social-target@example.com")
    target_profile = _create_profile(
        db_session,
        user=target_user,
        full_name="Admin Social Target",
        profile_status=ProfileStatus.HIDDEN,
        linkedin_url="https://linkedin.com/in/admin-social-target",
    )

    response = client.get(
        PROFILE_DETAIL_PATH.format(profile_id=target_profile.id),
        headers=_auth_headers("admin@example.com"),
    )

    assert response.status_code == 200
    assert response.json()["linkedin_url"] == "https://linkedin.com/in/admin-social-target"
