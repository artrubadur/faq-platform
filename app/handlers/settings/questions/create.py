# pyright: reportArgumentType=false
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.core.exceptions import SimilarityError
from app.dialogs.actions import SendAction
from app.dialogs.rows.base import ConfirmCallback
from app.dialogs.send.base import send_invalid
from app.dialogs.send.question import (
    send_confirm_creation,
    send_enter_answer_text,
    send_enter_question_text,
    send_found_similar,
    send_successfully_created,
)
from app.repositories.questions import QuestionsRepository
from app.services.question.process import (
    process_answer_text_msg,
    process_question_text_msg,
)
from app.services.question.service import QuestionsService
from app.storage.db.engine import async_session
from app.utils.history.last_message import LastMessage

from .root import DIR as PARENT_DIR

router = Router()

DIR = f"{PARENT_DIR}.create"


class Creation(StatesGroup):
    waiting_for_question_text = State()
    waiting_for_answer_text = State()


@router.callback_query(F.data == DIR)
async def question_create_cb_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    await send_enter_question_text(
        callback.message,
        SendAction.EDIT,
    )

    await state.set_state(Creation.waiting_for_question_text)


@router.message(Creation.waiting_for_question_text)
async def question_create_msg_question_text_handler(
    message: Message, last_message: LastMessage, state: FSMContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_question_text = await process_question_text_msg(message)
    except ValueError as e:
        sent_message = await send_invalid(
            message, SendAction.ANSWER, PARENT_DIR, str(e)
        )
        await last_message.set(sent_message, state)
        return

    await state.update_data(input_question_text=input_question_text)

    await send_enter_answer_text(message, SendAction.ANSWER)

    await state.set_state(Creation.waiting_for_answer_text)


@router.message(Creation.waiting_for_answer_text)
async def question_create_msg_answer_text_handler(
    message: Message, last_message: LastMessage, state: FSMContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_answer_text = await process_answer_text_msg(message)
    except ValueError as e:
        sent_message = await send_invalid(
            message, SendAction.ANSWER, PARENT_DIR, str(e)
        )
        await last_message.set(sent_message, state)
        return

    await state.update_data(input_answer_text=input_answer_text)

    data = await state.get_data()
    input_question_text: str = data["input_question_text"]

    await send_confirm_creation(
        message, SendAction.ANSWER, input_question_text, input_answer_text
    )

    await state.set_state(None)


@router.callback_query(ConfirmCallback.filter(F.dir == DIR and F.step == "create"))
async def question_create_cb_create_confirm_handler(
    callback: CallbackQuery, state: FSMContext
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    input_question_text: str = data["input_question_text"]
    input_answer_text: str = data["input_answer_text"]

    await state.update_data(input_id=None, input_username=None, input_role=None)

    async with async_session() as session:
        repo = QuestionsRepository(session)
        service = QuestionsService(repo)
        try:
            qustion = await service.create_question(
                input_question_text, input_answer_text, True
            )
            del data["input_question_text"], data["input_answer_text"]
            await send_successfully_created(
                callback.message,
                SendAction.EDIT,
                qustion.id,
                qustion.question_text,
                qustion.answer_text,
            )
        except SimilarityError as e:
            await send_found_similar(
                callback.message,
                SendAction.EDIT,
                e.question.id,
                e.question.question_text,
            )


@router.callback_query(ConfirmCallback.filter(F.dir == DIR and F.step == "similar"))
async def question_create_cb_similar_confirm_handler(
    callback: CallbackQuery, state: FSMContext
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    input_question_text: str = data.pop("input_question_text")
    input_answer_text: str = data.pop("input_answer_text")

    await state.update_data(input_id=None, input_username=None, input_role=None)

    async with async_session() as session:
        repo = QuestionsRepository(session)
        service = QuestionsService(repo)
        question = await service.create_question(
            input_question_text, input_answer_text, False
        )
        await send_successfully_created(
            callback.message,
            SendAction.EDIT,
            question.id,
            question.question_text,
            question.answer_text,
        )
