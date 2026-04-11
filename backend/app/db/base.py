# SQLAlchemy base metadata import point will be added later.
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.modules.users.models import User  # noqa: E402,F401
from app.modules.profiles.models import Profile, Preference  # noqa: E402,F401
from app.modules.media.models import IntroVideo, ProfilePhoto  # noqa: E402,F401 