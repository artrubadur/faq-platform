from aiogram import Router

from .ban_cmd import router as ban_cmd_router
from .error_cmd import router as error_cmd_router
from .goto_cmd import router as goto_cmd_router
from .settings import router as settings_router
from .state_cmd import router as state_cmd_router

router = Router()

router.include_router(settings_router)
router.include_router(state_cmd_router)
router.include_router(ban_cmd_router)
router.include_router(goto_cmd_router)
router.include_router(error_cmd_router)

__all__ = ["router"]
