from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from loguru import logger

from bot.core.config import config
from bot.core.customization import messages
from bot.dialogs import SendAction
from bot.dialogs.send.public.ask import send_failed, send_similar
from bot.services.question.gateway import question_gateway
from bot.services.question.process import (
    process_question_text_cmd,
    process_question_text_msg,
)

router = Router()


async def process_ask_handler(
    message: Message,
    question_text: str,
    *,
    send_action: SendAction,
):
    suggestion = await question_gateway.suggest_questions(
        question_text,
        config.questions.max_similar_amount,
        config.questions.max_popular_amount,
        config.questions.max_amount,
    )

    if not suggestion.is_confident:
        logger.debug("Failed to answer user", tg_id=message.from_user.id)
        await send_failed(
            message,
            SendAction.ANSWER,
            message,
            messages.exceptions.search.not_found,
            suggestion.questions,
        )
        return

    logger.debug("Answered user", tg_id=message.from_user.id, text=question_text)
    await send_similar(message, send_action, message, suggestion.questions)


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
