from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import model modules after Base is defined so SQLAlchemy registers all
# mapped classes even when application code imports a single module directly.
import app.modules.users.models  # noqa: E402,F401
import app.modules.profiles.models  # noqa: E402,F401
import app.modules.media.models  # noqa: E402,F401
