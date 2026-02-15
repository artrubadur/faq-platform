from aiogram import Router

from .admin import router as admin_router
from .common import router as common_router
from .public import router as public_router

router = Router()

router.include_router(admin_router)
router.include_router(common_router)
router.include_router(public_router)

__all__ = ["router"]
