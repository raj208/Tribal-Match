from enum import StrEnum


class ProfileStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    HIDDEN = "hidden"
    DEACTIVATED = "deactivated"
    DELETED = "deleted"


class VerificationStatus(StrEnum):
    NOT_STARTED = "not_started"
    UPLOADED = "uploaded"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class InterestStatus(StrEnum):
    SENT = "sent"
    RECEIVED = "received"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class ModerationStatus(StrEnum):
    CLEAN = "clean"
    FLAGGED = "flagged"
    UNDER_REVIEW = "under_review"
    ACTION_TAKEN = "action_taken"
