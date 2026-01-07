from aiogram import Router

from .ask import router as ask_router
from .errors import router as errors_router
from .start import router as start_router

router = Router()

router.include_router(start_router)
router.include_router(ask_router)
router.include_router(errors_router)

__all__ = ["router"]
