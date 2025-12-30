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

router = Router()

PARENT_DIR = "settings.questions"
DIR = "settings.questions.create"


class Creation(StatesGroup):
    waiting_for_question_text = State()
    waiting_for_answer_text = State()


# Entry point
@router.callback_query(F.data == DIR)
async def user_create_cb_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await send_enter_question_text(
        callback.message,
        action=SendAction.EDIT,
    )
    await state.set_state(Creation.waiting_for_question_text)


# Question text
@router.message(Creation.waiting_for_question_text)
async def user_create_msg_question_text_handler(message: Message, state: FSMContext):
    try:
        input_question_text = await process_question_text_msg(message)
    except ValueError as e:
        await send_invalid(message, PARENT_DIR, str(e), action=SendAction.ANSWER)
        return

    await state.update_data(input_question_text=input_question_text)

    await send_enter_answer_text(message, action=SendAction.ANSWER)
    await state.set_state(Creation.waiting_for_answer_text)


# Answer text
@router.message(Creation.waiting_for_answer_text)
async def user_create_msg_answer_text_handler(message: Message, state: FSMContext):
    try:
        input_answer_text = await process_answer_text_msg(message)
    except ValueError as e:
        await send_invalid(message, PARENT_DIR, str(e), action=SendAction.ANSWER)
        return

    await state.update_data(input_answer_text=input_answer_text)

    data = await state.get_data()
    input_question_text: str = data["input_question_text"]

    await send_confirm_creation(
        message, input_question_text, input_answer_text, action=SendAction.ANSWER
    )
    await state.set_state(None)


# Confirmation
@router.callback_query(ConfirmCallback.filter(F.dir == DIR and F.step == "create"))
async def user_create_cb_create_confirm_handler(
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
                qustion.id,
                qustion.question_text,
                qustion.answer_text,
                action=SendAction.EDIT,
            )
        except SimilarityError as e:
            await send_found_similar(
                callback.message,
                e.question.id,
                e.question.question_text,
                action=SendAction.EDIT,
            )


# Found similar
@router.callback_query(ConfirmCallback.filter(F.dir == DIR and F.step == "similar"))
async def user_create_cb_similar_confirm_handler(
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
        qustion = await service.create_question(
            input_question_text, input_answer_text, False
        )
        await send_successfully_created(
            callback.message,
            qustion.id,
            qustion.question_text,
            qustion.answer_text,
            action=SendAction.EDIT,
        )
