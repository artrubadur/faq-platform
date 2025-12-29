from aiogram import Router

from .root import router as root_router

router = Router()

router.include_router(root_router)

__all__ = ["router"]
