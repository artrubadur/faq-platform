from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger
from sqlalchemy.exc import NoResultFound

from app.core.constants.dirs import QUESTIONS_GET
from app.dialogs import SendAction
from app.dialogs.rows.question import IdCallback
from app.dialogs.send.admin.question import (
    send_enter_id,
    send_not_found,
    send_successfully_found,
)
from app.dialogs.send.common import send_invalid
from app.repositories.questions import QuestionsRepository
from app.services.question.process import process_id_msg
from app.services.question.service import QuestionsService
from app.storage.core import async_session
from app.utils.history.last_message import LastMessage

router = Router()

PARENT_DIR, DIR = QUESTIONS_GET


class QuestionFinding(StatesGroup):
    waiting_for_id = State()


@router.callback_query(F.data == DIR)
async def question_get_cb_handler(
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

    await state.set_state(QuestionFinding.waiting_for_id)


async def process_id_handler(
    message: Message, state: FSMContext, input_id: int, *, send_action: SendAction
):
    async with async_session() as session:
        repo = QuestionsRepository(session)
        service = QuestionsService(repo)
        try:
            question = await service.get_question(input_id)
        except NoResultFound:
            await send_not_found(message, send_action, input_id)
            return

    await state.update_data(glb_found_question_id=question.id)

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
        callback.message,  # pyright: ignore[reportArgumentType]bb
        state,
        input_id,
        send_action=SendAction.EDIT,
    )
