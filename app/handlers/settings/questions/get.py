# pyright: reportArgumentType=false
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.exc import NoResultFound

from app.dialogs import SendAction
from app.dialogs.rows.question import IdCallback
from app.dialogs.send.base import send_invalid
from app.dialogs.send.question import (
    send_enter_id,
    send_not_found,
    send_successfully_found,
)
from app.repositories.questions import QuestionsRepository
from app.services.question.process import process_id_msg
from app.services.question.service import QuestionsService
from app.storage.db.engine import async_session
from app.utils.history.last_message import LastMessage

from .root import DIR as PARENT_DIR

router = Router()

DIR = f"{PARENT_DIR}.get"


class Finding(StatesGroup):
    waiting_for_id = State()


@router.callback_query(F.data == DIR)
async def question_get_cb_handler(
    callback: CallbackQuery, last_message: LastMessage, state: FSMContext
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    found_question_id: int | None = data.get("found_question_id", None)

    sent_message = await send_enter_id(
        callback.message, SendAction.EDIT, DIR, found_question_id
    )
    await last_message.set(sent_message, state)

    await state.set_state(Finding.waiting_for_id)


async def process_id_handler(
    message: Message, state: FSMContext, input_id: int, *, send_action: SendAction
):
    async with async_session() as session:
        repo = QuestionsRepository(session)
        service = QuestionsService(repo)
        try:
            question = await service.read_question(input_id)
            await state.update_data(found_question_id=question.id)
            await send_successfully_found(
                message,
                send_action,
                question.id,
                question.question_text,
                question.answer_text,
            )
        except NoResultFound:
            await send_not_found(message, send_action, input_id)

    await state.set_state(None)


@router.message(Finding.waiting_for_id)
async def question_get_msg_id_handler(
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
async def question_get_cb_id_handler(
    callback: CallbackQuery, callback_data: IdCallback, state: FSMContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    input_id = callback_data.id

    await process_id_handler(
        callback.message, state, input_id, send_action=SendAction.EDIT
    )
