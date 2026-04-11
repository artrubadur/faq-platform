from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger

from bot.core.dirs import QUESTIONS_CREATE
from bot.dialogs.actions import SendAction
from bot.dialogs.rows.common import ConfirmCallback
from bot.dialogs.send.admin.question import (
    send_confirm_creation,
    send_embedding_failed,
    send_enter_answer_text,
    send_enter_question_text,
    send_found_similar,
    send_successfully_created,
)
from bot.dialogs.send.common import send_expired, send_invalid
from bot.services.question.gateway import question_gateway
from bot.services.question.process import (
    process_answer_text_msg,
    process_question_text_msg,
)
from bot.utils.state.history import LastMessage, is_expired
from bot.utils.state.temp import TempContext
from shared.api.exceptions import BadGatewayError, ConflictError

router = Router()

PARENT_DIR, DIR = QUESTIONS_CREATE


class QuestionCreation(StatesGroup):
    waiting_for_question_text = State()
    waiting_for_answer_text = State()


@router.callback_query(F.data == DIR)
async def question_create_cb_handler(
    callback: CallbackQuery, last_message: LastMessage, state: TempContext
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    sent_message = await send_enter_question_text(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        PARENT_DIR,
    )
    await last_message.set(sent_message, state)

    await state.set_data({"in_operation": True})
    await state.set_state(QuestionCreation.waiting_for_question_text)


@router.message(QuestionCreation.waiting_for_question_text)
async def question_create_msg_question_text_handler(
    message: Message, last_message: LastMessage, state: TempContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_question_text = process_question_text_msg(message)
    except ValueError as exc:
        sent_message = await send_invalid(
            message, SendAction.ANSWER, PARENT_DIR, str(exc)
        )
        await last_message.set(sent_message, state)
        return

    await state.update_data(input_question_text=input_question_text)

    sent_message = await send_enter_answer_text(message, SendAction.ANSWER, PARENT_DIR)
    await last_message.set(sent_message, state)

    await state.set_state(QuestionCreation.waiting_for_answer_text)


@router.message(QuestionCreation.waiting_for_answer_text)
async def question_create_msg_answer_text_handler(
    message: Message, last_message: LastMessage, state: TempContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_answer_text = process_answer_text_msg(message)
    except ValueError as exc:
        sent_message = await send_invalid(
            message, SendAction.ANSWER, PARENT_DIR, str(exc)
        )
        await last_message.set(sent_message, state)
        return

    await state.update_data(input_answer_text=input_answer_text)

    data = await state.get_data()
    if is_expired(data):
        await state.clear()
        return await send_expired(
            message,
            SendAction.ANSWER,
            PARENT_DIR,
        )
    await state.set_data(data)

    input_question_text: str = data["input_question_text"]

    await send_confirm_creation(
        message, SendAction.ANSWER, input_question_text, input_answer_text
    )

    await state.set_state(None)


@router.callback_query(ConfirmCallback.filter(F.dir == DIR and F.step == "create"))
async def question_create_cb_create_confirm_handler(
    callback: CallbackQuery, state: TempContext
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    if is_expired(data):
        await state.clear()
        return await send_expired(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.ANSWER,
            PARENT_DIR,
        )
    await state.set_data(data)

    input_question_text: str = data["input_question_text"]
    input_answer_text: str = data["input_answer_text"]

    try:
        question = await question_gateway.create_question(
            input_question_text,
            input_answer_text,
            True,
        )
    except ConflictError as exc:
        return await send_found_similar(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.EDIT,
            exc.data["id"],
            exc.data["question_text"],
        )
    except BadGatewayError:
        return await send_embedding_failed(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.ANSWER,
            PARENT_DIR,
        )

    logger.debug("Question created", id=question.id)
    await send_successfully_created(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        question.id,
        question.question_text,
        question.answer_text,
    )


@router.callback_query(ConfirmCallback.filter(F.dir == DIR and F.step == "similar"))
async def question_create_cb_similar_confirm_handler(
    callback: CallbackQuery, state: TempContext
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    if is_expired(data):
        await state.clear()
        return await send_expired(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.ANSWER,
            PARENT_DIR,
        )

    input_question_text: str = data["input_question_text"]
    input_answer_text: str = data["input_answer_text"]

    try:
        question = await question_gateway.create_question(
            input_question_text,
            input_answer_text,
            False,
        )
    except BadGatewayError:
        await state.clear()
        return await send_embedding_failed(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.ANSWER,
            PARENT_DIR,
        )

    await state.clear()

    logger.debug("Question created", id=question.id)
    await send_successfully_created(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        question.id,
        question.question_text,
        question.answer_text,
    )
