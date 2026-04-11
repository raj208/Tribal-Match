from fastapi import APIRouter

from app.api.meta import router as meta_router
from app.modules.auth.routes import router as auth_router
from app.modules.users.routes import router as users_router
from app.modules.profiles.routes import router as profiles_router
from app.modules.media.routes import router as media_router
from app.modules.discovery.routes import router as discovery_router
from app.modules.interests.routes import router as interests_router
from app.modules.verification.routes import router as verification_router
from app.modules.moderation.routes import router as moderation_router
from app.modules.settings.routes import router as settings_router
from app.modules.notifications.routes import router as notifications_router

api_router = APIRouter()

api_router.include_router(meta_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(profiles_router)
api_router.include_router(media_router)
api_router.include_router(discovery_router)
api_router.include_router(interests_router)
api_router.include_router(verification_router)
api_router.include_router(moderation_router)
api_router.include_router(settings_router)
api_router.include_router(notifications_router)