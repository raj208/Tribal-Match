try:
    from enum import StrEnum
except ImportError:
    from enum import Enum

    class StrEnum(str, Enum):
        def __str__(self) -> str:
            return str(self.value)


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
    ACCEPTED = "accepted"
    DECLINED = "declined"


class ModerationStatus(StrEnum):
    CLEAN = "clean"
    FLAGGED = "flagged"
    UNDER_REVIEW = "under_review"
    ACTION_TAKEN = "action_taken"


class ReportStatus(StrEnum):
    OPEN = "open"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"


def enum_values(enum_cls: type[StrEnum]) -> list[str]:
    return [member.value for member in enum_cls]
