# pyright: reportArgumentType=false
from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.dialogs import SendAction
from app.dialogs.send.public.ask import send_invalid, send_similar
from app.repositories.questions import QuestionsRepository
from app.services.question.process import (
    process_question_text_cmd,
    process_question_text_msg,
)
from app.services.question.service import QuestionsService
from app.storage.engine import async_session

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
        similar_questions = await service.get_similar(question_text, True)
        if len(similar_questions) == 0:
            await send_invalid(
                message,
                send_action,
                "It seems that we failed to understand the question",
            )
            return
        await send_similar(message, send_action, similar_questions)


@router.message(Command("ask"))
async def cmd_handler(message: Message, command: CommandObject):
    try:
        input_question_text = await process_question_text_cmd(command)
    except ValueError as e:
        await send_invalid(message, SendAction.ANSWER, str(e))
        return

    await process_ask_handler(
        message, input_question_text, send_action=SendAction.ANSWER
    )


@router.message()
async def msg_handler(message: Message):
    try:
        input_question_text = await process_question_text_msg(message)
    except ValueError as e:
        await send_invalid(message, SendAction.ANSWER, str(e))
        return

    await process_ask_handler(
        message, input_question_text, send_action=SendAction.ANSWER
    )
