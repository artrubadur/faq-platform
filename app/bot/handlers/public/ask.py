from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from loguru import logger

from app.core.config import config
from app.core.customization import messages
from app.dialogs import SendAction
from app.dialogs.send.public.ask import send_failed, send_similar
from app.repositories.questions import QuestionsRepository
from app.services.question.process import (
    process_question_text_cmd,
    process_question_text_msg,
)
from app.services.question.service import QuestionsService
from app.storage.instance import async_session

router = Router()


async def process_ask_handler(
    message: Message,
    question_text: str,
    *,
    send_action: SendAction,
):
    async with async_session() as session:
        repo = QuestionsRepository(session)
        service = QuestionsService(repo)

        suggestions, is_confident = await service.suggest_questions(
            question_text,
            config.questions.max_similar_amount,
            config.questions.max_popular_amount,
            config.questions.max_amount,
        )

    if not is_confident:
        logger.debug("Failed to answer user", tg_id=message.from_user.id)
        await send_failed(
            message,
            SendAction.ANSWER,
            message,
            messages.exceptions.search.not_found,
            suggestions,
        )
        return

    logger.debug("Answered user", tg_id=message.from_user.id, text=question_text)
    await send_similar(message, send_action, message, suggestions)


@router.message(Command("ask"))
async def cmd_handler(message: Message, command: CommandObject):
    try:
        input_question_text = process_question_text_cmd(command)
    except ValueError as exc:
        await send_failed(message, SendAction.ANSWER, message, str(exc))
        return

    await process_ask_handler(
        message, input_question_text, send_action=SendAction.ANSWER
    )


@router.message()
async def msg_handler(message: Message):
    try:
        input_question_text = process_question_text_msg(message)
    except ValueError as exc:
        await send_failed(message, SendAction.ANSWER, message, str(exc))
        return

    await process_ask_handler(
        message, input_question_text, send_action=SendAction.ANSWER
    )
