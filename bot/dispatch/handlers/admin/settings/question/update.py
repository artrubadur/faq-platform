from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger

from bot.core.dirs import QUESTIONS_UPDATE
from bot.dialogs import SendAction
from bot.dialogs.rows.common import (
    BackCallback,
    CancelCallback,
    ConfirmCallback,
    EditCallback,
    SaveCallback,
)
from bot.dialogs.rows.question import IdCallback
from bot.dialogs.send.admin.question import (
    send_changes,
    send_confirm_update,
    send_embedding_failed,
    send_enter_answer_text,
    send_enter_generation_amount,
    send_enter_id,
    send_enter_question_text,
    send_enter_rating,
    send_formulations_generation_failed,
    send_formulations_generation_unavailable,
    send_generation_amount_limit_exceeded,
    send_not_found,
    send_successfully_updated,
)
from bot.dialogs.send.common import send_expired, send_invalid
from bot.services.question.gateway import question_gateway
from bot.services.question.process import (
    process_answer_text_msg,
    process_generation_amount_msg,
    process_id_msg,
    process_question_text_msg,
    process_rating_msg,
)
from bot.utils.state.history import LastMessage, is_expired
from bot.utils.state.temp import TempContext
from shared.api.exceptions import (
    BadGatewayError,
    NotFoundError,
    TemporaryUnavailableError,
    ValidationError,
)
from shared.contracts.question.requests import UpdateQuestionRequest

router = Router()

PARENT_DIR, DIR = QUESTIONS_UPDATE


class QuestionUpdate(StatesGroup):
    waiting_for_id = State()
    waiting_for_question_text = State()
    waiting_for_answer_text = State()
    waiting_for_generation_amount = State()
    waiting_for_rating = State()


def _is_formulation_generation_error(exc: Exception) -> bool:
    data = getattr(exc, "data", None)
    return isinstance(data, dict) and data.get("scope") == "formulation_generation"


def _extract_generation_limit(exc: ValidationError) -> int | None:
    if not _is_formulation_generation_error(exc):
        return None

    max_amount = exc.data["max_amount"]
    return max_amount if isinstance(max_amount, int) else None


@router.callback_query(F.data == DIR)
async def question_update_cb_handler(
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
        PARENT_DIR,
        DIR,
        found_question_id,
    )
    await last_message.set(sent_message, state)

    await state.update_data({"in_operation": True})
    await state.set_state(QuestionUpdate.waiting_for_id)


async def process_id_handler(
    message: Message, state: TempContext, input_id: int, *, send_action: SendAction
):
    try:
        question = await question_gateway.get_question(input_id)
    except NotFoundError:
        await send_not_found(message, send_action, input_id)
        await state.set_state(None)
        return

    await state.update_data(
        orig_id=question.id,
        orig_question_text=question.question_text,
        orig_answer_text=question.answer_text,
        orig_rating=question.rating,
    )
    await send_confirm_update(
        message,
        send_action,
        question.id,
        question.question_text,
        question.answer_text,
    )

    await state.set_state(None)


@router.message(QuestionUpdate.waiting_for_id)
async def question_update_msg_id_handler(
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
async def question_update_cb_id_handler(
    callback: CallbackQuery, callback_data: IdCallback, state: TempContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    input_id = callback_data.id

    await process_id_handler(
        callback.message,  # pyright: ignore[reportArgumentType]
        state,
        input_id,
        send_action=SendAction.EDIT,
    )


async def process_fields_handler(
    message: Message, state: TempContext, *, send_action: SendAction
):
    data = await state.get_data()
    if is_expired(data):
        await state.clear()
        return await send_expired(
            message,
            SendAction.ANSWER,
            PARENT_DIR,
        )
    await state.set_data(data)

    id: int = data["orig_id"]
    question_text: str = data["orig_question_text"]
    answer_text: str = data["orig_answer_text"]
    rating: float = data["orig_rating"]

    edited_question_text: str = data.get("edited_question_text", question_text)
    edited_answer_text: str = data.get("edited_answer_text", answer_text)
    edited_rating: float = data.get("edited_rating", rating)
    input_generation_amount: int = data.get("input_generation_amount", 0)

    await send_changes(
        message,
        send_action,
        id,
        question_text,
        edited_question_text,
        answer_text,
        edited_answer_text,
        rating,
        edited_rating,
        input_generation_amount,
    )


@router.callback_query(ConfirmCallback.filter((F.dir == DIR) & (F.step == "update")))
async def question_update_confirm_cb_fields_handler(
    callback: CallbackQuery, state: TempContext
):
    await callback.answer()
    await process_fields_handler(
        callback.message,  # pyright: ignore[reportArgumentType]
        state,
        send_action=SendAction.EDIT,
    )


@router.callback_query(CancelCallback.filter(F.dir == PARENT_DIR))
async def question_update_cancel_cb_fields_handler(
    callback: CallbackQuery, state: TempContext
):
    await callback.answer()
    await process_fields_handler(
        callback.message,  # pyright: ignore[reportArgumentType]
        state,
        send_action=SendAction.EDIT,
    )


@router.callback_query(BackCallback.filter(F.dir == DIR))
async def question_update_back_cb_fields_handler(
    callback: CallbackQuery, state: TempContext
):
    await callback.answer()
    await process_fields_handler(
        callback.message,  # pyright: ignore[reportArgumentType]
        state,
        send_action=SendAction.EDIT,
    )


@router.callback_query(
    EditCallback.filter((F.dir == DIR) & (F.field == "question_text"))
)
async def question_update_cb_edit_question_text_handler(
    callback: CallbackQuery, last_message: LastMessage, state: TempContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    sent_message = await send_enter_question_text(
        callback.message, SendAction.EDIT, DIR  # pyright: ignore[reportArgumentType]
    )
    await last_message.set(sent_message, state)

    await state.set_state(QuestionUpdate.waiting_for_question_text)


@router.message(QuestionUpdate.waiting_for_question_text)
async def question_update_msg_edited_question_text_handler(
    message: Message, last_message: LastMessage, state: TempContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_question_text = process_question_text_msg(message)
    except ValueError as exc:
        sent_message = await send_invalid(message, SendAction.ANSWER, DIR, str(exc))
        await last_message.set(sent_message, state)
        return

    await state.update_data(edited_question_text=input_question_text)

    await process_fields_handler(message, state, send_action=SendAction.ANSWER)

    await state.set_state(None)


@router.callback_query(EditCallback.filter((F.dir == DIR) & (F.field == "answer_text")))
async def question_update_cb_edit_answer_text_handler(
    callback: CallbackQuery, last_message: LastMessage, state: TempContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    sent_message = await send_enter_answer_text(
        callback.message, SendAction.EDIT, DIR  # pyright: ignore[reportArgumentType]
    )
    await last_message.set(sent_message, state)

    await state.set_state(QuestionUpdate.waiting_for_answer_text)


@router.message(QuestionUpdate.waiting_for_answer_text)
async def question_update_msg_edited_answer_text_handler(
    message: Message, last_message: LastMessage, state: TempContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_answer_text = process_answer_text_msg(message)
    except ValueError as exc:
        sent_message = await send_invalid(message, SendAction.ANSWER, DIR, str(exc))
        await last_message.set(sent_message, state)
        return

    await state.update_data(edited_answer_text=input_answer_text)

    await process_fields_handler(message, state, send_action=SendAction.ANSWER)

    await state.set_state(None)


@router.callback_query(EditCallback.filter((F.dir == DIR) & (F.field == "rating")))
async def question_update_cb_edit_rating_handler(
    callback: CallbackQuery, last_message: LastMessage, state: TempContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    sent_message = await send_enter_rating(
        callback.message, SendAction.EDIT, DIR  # pyright: ignore[reportArgumentType]
    )
    await last_message.set(sent_message, state)

    await state.set_state(QuestionUpdate.waiting_for_rating)


@router.callback_query(
    EditCallback.filter((F.dir == DIR) & (F.field == "generation_amount"))
)
async def question_update_cb_edit_generation_amount_handler(
    callback: CallbackQuery, last_message: LastMessage, state: TempContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    sent_message = await send_enter_generation_amount(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        DIR,
    )
    await last_message.set(sent_message, state)

    await state.set_state(QuestionUpdate.waiting_for_generation_amount)


@router.message(QuestionUpdate.waiting_for_generation_amount)
async def question_update_msg_generation_amount_handler(
    message: Message,
    last_message: LastMessage,
    state: TempContext,
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_generation_amount = process_generation_amount_msg(message)
    except ValueError as exc:
        sent_message = await send_invalid(message, SendAction.ANSWER, DIR, str(exc))
        await last_message.set(sent_message, state)
        return

    await state.update_data(input_generation_amount=input_generation_amount)

    await process_fields_handler(message, state, send_action=SendAction.ANSWER)
    await state.set_state(None)


@router.message(QuestionUpdate.waiting_for_rating)
async def question_update_msg_edited_rating_handler(
    message: Message, last_message: LastMessage, state: TempContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_rating = process_rating_msg(message)
    except ValueError as exc:
        sent_message = await send_invalid(message, SendAction.ANSWER, DIR, str(exc))
        await last_message.set(sent_message, state)
        return

    await state.update_data(edited_rating=input_rating)

    await process_fields_handler(message, state, send_action=SendAction.ANSWER)

    await state.set_state(None)


@router.callback_query(SaveCallback.filter(F.dir == DIR))
async def question_update_cb_save_handler(callback: CallbackQuery, state: TempContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    if is_expired(data):
        await state.clear()
        await send_expired(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.ANSWER,
            PARENT_DIR,
        )
        return

    id: int = data["orig_id"]

    edited_question_text: str | None = data.get("edited_question_text", None)
    edited_answer_text: str | None = data.get("edited_answer_text", None)
    edited_rating: float | None = data.get("edited_rating", None)
    input_generation_amount: int | None = data.get("input_generation_amount", None)

    request = UpdateQuestionRequest(
        question_text=edited_question_text,
        answer_text=edited_answer_text,
        rating=edited_rating,
        generate_formulations_amount=input_generation_amount,
    )

    try:
        question = await question_gateway.update_question(
            id,
            **request.model_dump(mode="json", exclude_none=True),
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
    except NotFoundError:
        await state.clear()
        return await send_not_found(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.EDIT,
            id,
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

    logger.debug("Question updated", id=question.id)
    await send_successfully_updated(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        question.id,
        question.question_text,
        question.answer_text,
        question.rating,
        question.formulation_ids if len(question.formulation_ids) > 0 else None,
    )
