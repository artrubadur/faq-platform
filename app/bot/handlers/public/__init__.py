from aiogram import Router

from .ask import router as ask_cmd_router
from .commands import router as commands_router
from .errors import router as errors_router
from .start_cmd import router as start_cmd_router

router = Router()

router.include_router(start_cmd_router)
router.include_router(errors_router)
router.include_router(commands_router)
# Should be last
router.include_router(ask_cmd_router)

__all__ = ["router"]
