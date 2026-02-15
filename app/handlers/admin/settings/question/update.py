from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger
from sqlalchemy.exc import NoResultFound

from app.core.constants.dirs import QUESTIONS_UPDATE
from app.dialogs import SendAction
from app.dialogs.rows.common import (
    BackCallback,
    CancelCallback,
    ConfirmCallback,
    EditCallback,
    SaveCallback,
)
from app.dialogs.rows.question import IdCallback
from app.dialogs.send.admin.question import (
    send_changes,
    send_confirm_recompute,
    send_confirm_update,
    send_edit_answer_text,
    send_edit_question_text,
    send_edit_rating,
    send_enter_id,
    send_not_found,
    send_successfully_updated,
)
from app.dialogs.send.common import send_invalid
from app.repositories.questions import QuestionsRepository
from app.services.question.process import (
    process_answer_text_msg,
    process_id_msg,
    process_question_text_msg,
    process_rating_msg,
)
from app.services.question.service import QuestionsService
from app.storage.core import async_session
from app.utils.history.last_message import LastMessage

router = Router()

PARENT_DIR, DIR = QUESTIONS_UPDATE


class QuestionUpdate(StatesGroup):
    waiting_for_id = State()
    waiting_for_question_text = State()
    waiting_for_answer_text = State()
    waiting_for_rating = State()


@router.callback_query(F.data == DIR)
async def question_update_cb_handler(
    callback: CallbackQuery, last_message: LastMessage, state: FSMContext
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    found_question_id: int | None = data.get("glb_found_question_id", None)

    sent_message = await send_enter_id(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        DIR,
        PARENT_DIR,
        found_question_id,
    )
    await last_message.set(sent_message, state)

    await state.set_state(QuestionUpdate.waiting_for_id)


async def process_id_handler(
    message: Message, state: FSMContext, input_id: int, *, send_action: SendAction
):
    async with async_session() as session:
        repo = QuestionsRepository(session)
        service = QuestionsService(repo)
        try:
            question = await service.get_question(input_id)
            await state.update_data(
                tmp_input_id=input_id,
                tmp_orig_question_text=question.question_text,
                tmp_orig_answer_text=question.answer_text,
                tmp_orig_rating=question.rating,
            )
            await send_confirm_update(
                message,
                send_action,
                question.id,
                question.question_text,
                question.answer_text,
            )
        except NoResultFound:
            await send_not_found(message, send_action, input_id)

    await state.set_state(None)


@router.message(QuestionUpdate.waiting_for_id)
async def question_update_msg_id_handler(
    message: Message, last_message: LastMessage, state: FSMContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_id = await process_id_msg(message)
    except ValueError as e:
        sent_message = await send_invalid(
            message, SendAction.ANSWER, PARENT_DIR, str(e)
        )
        await last_message.set(sent_message, state)
        return

    await process_id_handler(message, state, input_id, send_action=SendAction.ANSWER)


@router.callback_query(IdCallback.filter(F.dir == DIR))
async def question_update_cb_id_handler(
    callback: CallbackQuery, callback_data: IdCallback, state: FSMContext
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
    message: Message, state: FSMContext, *, send_action: SendAction
):
    data = await state.get_data()
    id: int = data["tmp_input_id"]
    question_text: str = data["tmp_orig_question_text"]
    answer_text: str = data["tmp_orig_answer_text"]
    rating: float = data["tmp_orig_rating"]

    edited_question_text: str = data.get("tmp_edited_question_text", question_text)
    edited_answer_text: str = data.get("tmp_edited_answer_text", answer_text)
    edited_rating: float = data.pop("tmp_edited_rating", rating)

    recompute_embedding: bool = data.get("tmp_recompute_embedding", False)

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
        recompute_embedding,
    )


@router.callback_query(ConfirmCallback.filter((F.dir == DIR) & (F.step == "update")))
async def question_update_confirm_cb_fields_handler(
    callback: CallbackQuery, state: FSMContext
):
    await callback.answer()
    await process_fields_handler(
        callback.message,  # pyright: ignore[reportArgumentType]
        state,
        send_action=SendAction.EDIT,
    )


@router.callback_query(CancelCallback.filter(F.dir == PARENT_DIR))
async def question_update_cancel_cb_fields_handler(
    callback: CallbackQuery, state: FSMContext
):
    await callback.answer()
    await process_fields_handler(
        callback.message,  # pyright: ignore[reportArgumentType]
        state,
        send_action=SendAction.EDIT,
    )


@router.callback_query(BackCallback.filter(F.dir == DIR))
async def question_update_back_cb_fields_handler(
    callback: CallbackQuery, state: FSMContext
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
    callback: CallbackQuery, last_message: LastMessage, state: FSMContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    sent_message = await send_edit_question_text(
        callback.message, SendAction.EDIT, DIR  # pyright: ignore[reportArgumentType]
    )
    await last_message.set(sent_message, state)

    await state.set_state(QuestionUpdate.waiting_for_question_text)


@router.message(QuestionUpdate.waiting_for_question_text)
async def question_update_msg_edited_question_text_handler(
    message: Message, last_message: LastMessage, state: FSMContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_question_text = await process_question_text_msg(message)
    except ValueError as e:
        sent_message = await send_invalid(message, SendAction.ANSWER, DIR, str(e))
        await last_message.set(sent_message, state)
        return

    await state.update_data(tmp_edited_question_text=input_question_text)

    await send_confirm_recompute(message, SendAction.ANSWER)

    await state.set_state(None)


@router.callback_query(ConfirmCallback.filter((F.dir == DIR) & (F.step == "recompute")))
async def question_update_cb_confirm_recompute_handler(
    callback: CallbackQuery, state: FSMContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    await state.update_data(tmp_recompute_embedding=True)

    await process_fields_handler(
        callback.message,  # pyright: ignore[reportArgumentType]
        state,
        send_action=SendAction.EDIT,
    )


@router.callback_query(CancelCallback.filter(F.dir == DIR))
async def question_update_cb_cancel_recompute_handler(
    callback: CallbackQuery, state: FSMContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    await state.update_data(tmp_recompute_embedding=False)

    await process_fields_handler(
        callback.message,  # pyright: ignore[reportArgumentType]
        state,
        send_action=SendAction.EDIT,
    )


@router.callback_query(EditCallback.filter((F.dir == DIR) & (F.field == "answer_text")))
async def question_update_cb_edit_answer_text_handler(
    callback: CallbackQuery, last_message: LastMessage, state: FSMContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    sent_message = await send_edit_answer_text(
        callback.message, SendAction.EDIT, DIR  # pyright: ignore[reportArgumentType]
    )
    await last_message.set(sent_message, state)

    await state.set_state(QuestionUpdate.waiting_for_answer_text)


@router.message(QuestionUpdate.waiting_for_answer_text)
async def question_update_msg_edited_answer_text_handler(
    message: Message, last_message: LastMessage, state: FSMContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_answer_text = await process_answer_text_msg(message)
    except ValueError as e:
        sent_message = await send_invalid(message, SendAction.ANSWER, DIR, str(e))
        await last_message.set(sent_message, state)
        return

    await state.update_data(tmp_edited_answer_text=input_answer_text)

    await process_fields_handler(message, state, send_action=SendAction.ANSWER)

    await state.set_state(None)


@router.callback_query(EditCallback.filter((F.dir == DIR) & (F.field == "rating")))
async def question_update_cb_edit_rating_handler(
    callback: CallbackQuery, last_message: LastMessage, state: FSMContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    sent_message = await send_edit_rating(
        callback.message, SendAction.EDIT, DIR  # pyright: ignore[reportArgumentType]
    )
    await last_message.set(sent_message, state)

    await state.set_state(QuestionUpdate.waiting_for_rating)


@router.message(QuestionUpdate.waiting_for_rating)
async def question_update_msg_edited_rating_handler(
    message: Message, last_message: LastMessage, state: FSMContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_rating = await process_rating_msg(message)
    except ValueError as e:
        sent_message = await send_invalid(message, SendAction.ANSWER, DIR, str(e))
        await last_message.set(sent_message, state)
        return

    await state.update_data(tmp_edited_rating=input_rating)

    await process_fields_handler(message, state, send_action=SendAction.ANSWER)

    await state.set_state(None)


@router.callback_query(SaveCallback.filter(F.dir == DIR))
async def question_update_cb_save_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    id: int = data.pop("tmp_input_id")
    question_text: str = data.pop("tmp_orig_question_text")
    answer_text: str = data.pop("tmp_orig_answer_text")
    rating: float = data.pop("tmp_orig_rating")

    edited_question_text: str = data.pop("tmp_edited_question_text", question_text)
    edited_answer_text: str = data.pop("tmp_edited_answer_text", answer_text)
    edited_rating: float = data.pop("tmp_edited_rating", rating)

    recompute_embedding: bool = data.pop("tmp_recompute_embedding", False)
    await state.set_data(data)

    async with async_session() as session:
        repo = QuestionsRepository(session)
        service = QuestionsService(repo)
        try:
            question = await service.update_question(
                id,
                edited_question_text,
                edited_answer_text,
                edited_rating,
                recompute_embedding,
            )
            logger.debug("Question updated", id=question.id)
            await send_successfully_updated(
                callback.message,  # pyright: ignore[reportArgumentType]
                SendAction.EDIT,
                question.id,
                question.question_text,
                question.answer_text,
                question.rating
            )
        except NoResultFound:
            await send_not_found(
                callback.message,  # pyright: ignore[reportArgumentType]
                SendAction.EDIT,
                id,
            )
