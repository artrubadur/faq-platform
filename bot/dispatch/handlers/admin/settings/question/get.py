from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger

from bot.core.dirs import QUESTIONS_GET
from bot.dialogs import SendAction
from bot.dialogs.rows.question import IdCallback
from bot.dialogs.send.admin.question import (
    send_enter_id,
    send_not_found,
    send_successfully_found,
)
from bot.dialogs.send.common import send_invalid
from bot.services.api.exceptions import NotFoundError
from bot.services.question.gateway import question_gateway
from bot.services.question.process import process_id_msg
from bot.utils.state.history import LastMessage
from bot.utils.state.temp import TempContext

router = Router()

PARENT_DIR, DIR = QUESTIONS_GET


class QuestionFinding(StatesGroup):
    waiting_for_id = State()


@router.callback_query(F.data == DIR)
async def question_get_cb_handler(
    callback: CallbackQuery, last_message: LastMessage, state: TempContext
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    found_question_id: int | None = await state.storage.get_value(
        state.key, "found_question_id", None, "long"
    )

    sent_message = await send_enter_id(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        DIR,
        PARENT_DIR,
        found_question_id,
    )
    await last_message.set(sent_message, state)

    await state.set_state(QuestionFinding.waiting_for_id)


async def process_id_handler(
    message: Message, state: TempContext, input_id: int, *, send_action: SendAction
):
    try:
        question = await question_gateway.get_question(input_id)
    except NotFoundError:
        await send_not_found(message, send_action, input_id)
        await state.set_state(None)
        return

    await state.storage.update_data(
        state.key, {"found_question_id": question.id}, "long"
    )

    logger.debug("Question obtained", id=question.id)
    await send_successfully_found(
        message,
        send_action,
        question.id,
        question.question_text,
        question.answer_text,
    )

    await state.set_state(None)


@router.message(QuestionFinding.waiting_for_id)
async def question_get_msg_id_handler(
    message: Message, last_message: LastMessage, state: TempContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_id = process_id_msg(message)
    except ValueError as exc:
        sent_message = await send_invalid(
            message, SendAction.ANSWER, PARENT_DIR, str(exc)
        )
        await last_message.set(sent_message, state)
        return

    await process_id_handler(message, state, input_id, send_action=SendAction.ANSWER)


@router.callback_query(IdCallback.filter(F.dir == DIR))
async def question_get_cb_id_handler(
    callback: CallbackQuery, callback_data: IdCallback, state: TempContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    input_id = callback_data.id

    await process_id_handler(
        callback.message,  # pyright: ignore[reportArgumentType]bb
        state,
        input_id,
        send_action=SendAction.EDIT,
    )
