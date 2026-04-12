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
    send_enter_generation_amount,
    send_enter_question_text,
    send_formulations_generation_failed,
    send_formulations_generation_unavailable,
    send_found_similar,
    send_generation_amount_limit_exceeded,
    send_successfully_created,
)
from bot.dialogs.send.common import send_expired, send_invalid
from bot.services.question.gateway import question_gateway
from bot.services.question.process import (
    process_answer_text_msg,
    process_generation_amount_msg,
    process_question_text_msg,
)
from bot.utils.state.history import LastMessage, is_expired
from bot.utils.state.temp import TempContext
from shared.api.exceptions import (
    BadGatewayError,
    ConflictError,
    TemporaryUnavailableError,
    ValidationError,
)

router = Router()

PARENT_DIR, DIR = QUESTIONS_CREATE


class QuestionCreation(StatesGroup):
    waiting_for_question_text = State()
    waiting_for_answer_text = State()
    waiting_for_generation_amount = State()


def _is_formulation_generation_error(exc: Exception) -> bool:
    data = getattr(exc, "data", None)
    return isinstance(data, dict) and data.get("scope") == "formulation_generation"


def _extract_generation_limit(exc: ValidationError) -> int | None:
    if not _is_formulation_generation_error(exc):
        return None

    max_amount = exc.data["max_amount"]
    return max_amount if isinstance(max_amount, int) else None


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

    data = await state.get_data()
    if is_expired(data):
        await state.clear()
        return await send_expired(
            message,
            SendAction.ANSWER,
            PARENT_DIR,
        )
    data["input_question_text"] = input_question_text
    await state.set_data(data)

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

    data = await state.get_data()
    if is_expired(data):
        await state.clear()
        return await send_expired(
            message,
            SendAction.ANSWER,
            PARENT_DIR,
        )
    data["input_answer_text"] = input_answer_text
    await state.set_data(data)

    sent_message = await send_enter_generation_amount(
        message,
        SendAction.ANSWER,
        PARENT_DIR,
    )
    await last_message.set(sent_message, state)

    await state.set_state(QuestionCreation.waiting_for_generation_amount)


@router.message(QuestionCreation.waiting_for_generation_amount)
async def question_create_msg_generation_amount_handler(
    message: Message, last_message: LastMessage, state: TempContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_generation_amount = process_generation_amount_msg(message)
    except ValueError as exc:
        sent_message = await send_invalid(
            message, SendAction.ANSWER, PARENT_DIR, str(exc)
        )
        await last_message.set(sent_message, state)
        return

    data = await state.get_data()
    if is_expired(data):
        await state.clear()
        return await send_expired(
            message,
            SendAction.ANSWER,
            PARENT_DIR,
        )
    data["input_generation_amount"] = input_generation_amount
    await state.set_data(data)

    input_question_text: str = data["input_question_text"]
    input_answer_text: str = data["input_answer_text"]
    input_generation_amount: int = data["input_generation_amount"]

    await send_confirm_creation(
        message,
        SendAction.ANSWER,
        input_question_text,
        input_answer_text,
        input_generation_amount,
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
    input_generation_amount: int = data["input_generation_amount"]

    try:
        question = await question_gateway.create_question(
            input_question_text,
            input_answer_text,
            True,
            input_generation_amount,
        )
    except ConflictError as exc:
        return await send_found_similar(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.EDIT,
            exc.data["id"],
            exc.data["question_text"],
        )
    except ValidationError as exc:
        await state.clear()
        if (max_amount := _extract_generation_limit(exc)) is not None:
            return await send_generation_amount_limit_exceeded(
                callback.message,  # pyright: ignore[reportArgumentType]
                SendAction.ANSWER,
                PARENT_DIR,
                max_amount,
            )
        return await send_invalid(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.ANSWER,
            PARENT_DIR,
            str(exc),
        )
    except TemporaryUnavailableError:
        await state.clear()
        return await send_formulations_generation_unavailable(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.ANSWER,
            PARENT_DIR,
        )
    except BadGatewayError as exc:
        await state.clear()
        if _is_formulation_generation_error(exc):
            return await send_formulations_generation_failed(
                callback.message,  # pyright: ignore[reportArgumentType]
                SendAction.ANSWER,
                PARENT_DIR,
            )
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
        question.formulation_ids if input_generation_amount > 0 else None,
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
    input_generation_amount: int = data["input_generation_amount"]

    try:
        question = await question_gateway.create_question(
            input_question_text,
            input_answer_text,
            False,
            input_generation_amount,
        )
    except ValidationError as exc:
        await state.clear()
        if (max_amount := _extract_generation_limit(exc)) is not None:
            return await send_generation_amount_limit_exceeded(
                callback.message,  # pyright: ignore[reportArgumentType]
                SendAction.ANSWER,
                PARENT_DIR,
                max_amount,
            )
        return await send_invalid(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.ANSWER,
            PARENT_DIR,
            str(exc),
        )
    except TemporaryUnavailableError:
        await state.clear()
        return await send_formulations_generation_unavailable(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.ANSWER,
            PARENT_DIR,
        )
    except BadGatewayError as exc:
        await state.clear()
        if _is_formulation_generation_error(exc):
            return await send_formulations_generation_failed(
                callback.message,  # pyright: ignore[reportArgumentType]
                SendAction.ANSWER,
                PARENT_DIR,
            )
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
        question.formulation_ids if len(question.formulation_ids) > 0 else None,
    )
