from aiogram import Router

from .root import router as root_router
from .settings import router as settings_router

router = Router()

router.include_router(root_router)
router.include_router(settings_router)

__all__ = ["router"]
