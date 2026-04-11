from aiogram import Router

from .formulation import router as formulations_router
from .question import router as questions_router
from .root import router as root_router
from .user import router as users_router

router = Router()

router.include_router(users_router)
router.include_router(questions_router)
router.include_router(formulations_router)
router.include_router(root_router)

__all__ = ["router"]
