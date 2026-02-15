from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from loguru import logger

from app.dialogs import SendAction
from app.dialogs.send.public.ask import send_failed, send_similar
from app.repositories.questions import QuestionsRepository
from app.services.question.process import (
    process_question_text_cmd,
    process_question_text_msg,
)
from app.services.question.service import QuestionsService
from app.storage.core import async_session

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

        similar_questions, _ = await service.get_similar_questions(question_text, 8)
        popular_questions = await service.get_most_popular_questions(
            8 - len(similar_questions), similar_questions
        )

    suggestion = similar_questions + popular_questions

    if len(similar_questions) == 0:
        logger.debug("Failed to answer user", tg_id=message.from_user.id)
        await send_failed(
            message,
            send_action,
            "It seems that we failed to understand the question",
            popular_questions,
        )
        return

    logger.debug("Answered user", tg_id=message.from_user.id, text=question_text)
    await send_similar(message, send_action, suggestion)


@router.message(Command("ask"))
async def cmd_handler(message: Message, command: CommandObject):
    try:
        input_question_text = await process_question_text_cmd(command)
    except ValueError as e:
        await send_failed(message, SendAction.ANSWER, str(e))
        return

    await process_ask_handler(
        message, input_question_text, send_action=SendAction.ANSWER
    )


@router.message()
async def msg_handler(message: Message):
    try:
        input_question_text = await process_question_text_msg(message)
    except ValueError as e:
        await send_failed(message, SendAction.ANSWER, str(e))
        return

    await process_ask_handler(
        message, input_question_text, send_action=SendAction.ANSWER
    )
