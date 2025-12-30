from aiogram import Router

from .create import router as create_router
from .get import router as get_router
from .root import router as root_router

router = Router()

router.include_router(root_router)
router.include_router(create_router)
router.include_router(get_router)

__all__ = ["router"]
