from aiogram import Router

from .questions import router as questions_router
from .root import router as root_router
from .users import router as users_router

router = Router()

router.include_router(users_router)
router.include_router(questions_router)
router.include_router(root_router)

__all__ = ["router"]
