from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.interests.models import Interest
from app.modules.moderation.models import Block
from app.modules.profiles.models import Profile
from app.modules.users.models import User
from app.shared.enums import InterestStatus, ProfileStatus

INTERESTS_PATH = f"{settings.api_v1_prefix}/interests"


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
    profile_status: ProfileStatus = ProfileStatus.PUBLISHED,
) -> Profile:
    profile = Profile(
        user_id=user.id,
        full_name=full_name,
        profile_status=profile_status,
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


def test_patch_interest_requires_auth(client) -> None:
    response = client.patch(
        f"{INTERESTS_PATH}/{uuid4()}",
        json={"action": "accept"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_patch_interest_returns_404_when_interest_is_missing(client) -> None:
    response = client.patch(
        f"{INTERESTS_PATH}/{uuid4()}",
        headers=_auth_headers("missing-interest@example.com"),
        json={"action": "accept"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Interest not found"}


@pytest.mark.parametrize(
    ("action", "expected_status"),
    [
        ("accept", InterestStatus.ACCEPTED),
        ("decline", InterestStatus.DECLINED),
    ],
)
def test_patch_interest_updates_status_for_receiver(
    client,
    db_session: Session,
    action: str,
    expected_status: InterestStatus,
) -> None:
    sender = _create_user(db_session, f"sender-{action}@example.com")
    receiver = _create_user(db_session, f"receiver-{action}@example.com")
    sender_profile = _create_profile(db_session, user=sender, full_name="Sender User")
    receiver_profile = _create_profile(db_session, user=receiver, full_name="Receiver User")
    interest = _create_interest(
        db_session,
        sender_user=sender,
        receiver_user=receiver,
        sender_profile=sender_profile,
        receiver_profile=receiver_profile,
    )

    response = client.patch(
        f"{INTERESTS_PATH}/{interest.id}",
        headers=_auth_headers(receiver.email),
        json={"action": action},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": str(interest.id),
        "status": expected_status.value,
    }

    refreshed_interest = db_session.get(Interest, interest.id)
    assert refreshed_interest is not None
    assert refreshed_interest.status == expected_status


def test_patch_interest_forbids_sender_from_acting_on_sent_interest(client, db_session: Session) -> None:
    sender = _create_user(db_session, "sender-own-interest@example.com")
    receiver = _create_user(db_session, "receiver-own-interest@example.com")
    sender_profile = _create_profile(db_session, user=sender, full_name="Sender User")
    receiver_profile = _create_profile(db_session, user=receiver, full_name="Receiver User")
    interest = _create_interest(
        db_session,
        sender_user=sender,
        receiver_user=receiver,
        sender_profile=sender_profile,
        receiver_profile=receiver_profile,
    )

    response = client.patch(
        f"{INTERESTS_PATH}/{interest.id}",
        headers=_auth_headers(sender.email),
        json={"action": "accept"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Only the receiver can act on this interest"}

    refreshed_interest = db_session.get(Interest, interest.id)
    assert refreshed_interest is not None
    assert refreshed_interest.status == InterestStatus.SENT


def test_patch_interest_returns_409_when_interest_was_already_acted_on(client, db_session: Session) -> None:
    sender = _create_user(db_session, "sender-processed-interest@example.com")
    receiver = _create_user(db_session, "receiver-processed-interest@example.com")
    sender_profile = _create_profile(db_session, user=sender, full_name="Sender User")
    receiver_profile = _create_profile(db_session, user=receiver, full_name="Receiver User")
    interest = _create_interest(
        db_session,
        sender_user=sender,
        receiver_user=receiver,
        sender_profile=sender_profile,
        receiver_profile=receiver_profile,
        status=InterestStatus.ACCEPTED,
    )

    response = client.patch(
        f"{INTERESTS_PATH}/{interest.id}",
        headers=_auth_headers(receiver.email),
        json={"action": "decline"},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Interest has already been acted on"}

    refreshed_interest = db_session.get(Interest, interest.id)
    assert refreshed_interest is not None
    assert refreshed_interest.status == InterestStatus.ACCEPTED


def test_patch_interest_respects_existing_block_rule(client, db_session: Session) -> None:
    sender = _create_user(db_session, "sender-blocked-interest@example.com")
    receiver = _create_user(db_session, "receiver-blocked-interest@example.com")
    sender_profile = _create_profile(db_session, user=sender, full_name="Sender User")
    receiver_profile = _create_profile(db_session, user=receiver, full_name="Receiver User")
    interest = _create_interest(
        db_session,
        sender_user=sender,
        receiver_user=receiver,
        sender_profile=sender_profile,
        receiver_profile=receiver_profile,
    )
    _create_block(db_session, blocker_user=receiver, blocked_user=sender)

    response = client.patch(
        f"{INTERESTS_PATH}/{interest.id}",
        headers=_auth_headers(receiver.email),
        json={"action": "accept"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Interaction unavailable for this profile"}

    refreshed_interest = db_session.get(Interest, interest.id)
    assert refreshed_interest is not None
    assert refreshed_interest.status == InterestStatus.SENT
