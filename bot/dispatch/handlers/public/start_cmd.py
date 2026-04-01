from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from loguru import logger

from bot.core.config import config
from bot.dialogs.actions import SendAction
from bot.dialogs.send.public.start import send_start
from bot.services.question.gateway import question_gateway
from bot.services.user.gateway import user_gateway
from shared.contracts.user.responses import Role
from shared.http.exceptions import ConflictError

router = Router()


@router.message(CommandStart())
async def cmd_handler(message: Message):
    try:
        suggestion = await question_gateway.suggest_questions(
            "",
            0,
            config.questions.max_popular_amount,
            config.questions.max_popular_amount,
        )
        questions = suggestion.questions
    except Exception:
        logger.exception("Failed to fetch popular questions")
        questions = []

    await send_start(message, SendAction.ANSWER, message, questions)

    try:
        tg_user = message.from_user
        db_user = await user_gateway.create_user(
            tg_user.id, tg_user.username, Role.USER
        )
        logger.debug("Newbie created", id=db_user.id, tg_id=db_user.telegram_id)
    except ConflictError:
        pass
