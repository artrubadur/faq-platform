from aiogram import Router

from .error import router as error_router
from .goto import router as goto_router
from .settings import router as settings_router
from .state import router as state_router

router = Router()

router.include_router(settings_router)
router.include_router(state_router)
router.include_router(goto_router)
router.include_router(error_router)

__all__ = ["router"]
