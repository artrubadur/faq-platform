from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger

from bot.core.dirs import FORMULATIONS_CREATE
from bot.dialogs import SendAction
from bot.dialogs.rows.common import ConfirmCallback
from bot.dialogs.send.admin.formulation import (
    send_confirm_creation,
    send_embedding_failed,
    send_enter_question_id,
    send_enter_question_text,
    send_successfully_created,
)
from bot.dialogs.send.common import send_expired, send_invalid
from bot.services.formulation.gateway import formulation_gateway
from bot.services.formulation.process import (
    process_question_id_msg,
    process_question_text_msg,
)
from bot.utils.state.history import LastMessage, is_expired
from bot.utils.state.temp import TempContext
from shared.api.exceptions import BadGatewayError, NotFoundError

router = Router()

PARENT_DIR, DIR = FORMULATIONS_CREATE


class FormulationCreation(StatesGroup):
    waiting_for_question_id = State()
    waiting_for_question_text = State()


@router.callback_query(F.data == DIR)
async def formulation_create_cb_handler(
    callback: CallbackQuery, last_message: LastMessage, state: TempContext
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    sent_message = await send_enter_question_id(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        PARENT_DIR,
    )
    await last_message.set(sent_message, state)

    await state.set_data({"in_operation": True})
    await state.set_state(FormulationCreation.waiting_for_question_id)


@router.message(FormulationCreation.waiting_for_question_id)
async def formulation_create_msg_question_id_handler(
    message: Message, last_message: LastMessage, state: TempContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_question_id = process_question_id_msg(message)
    except ValueError as exc:
        sent_message = await send_invalid(
            message, SendAction.ANSWER, PARENT_DIR, str(exc)
        )
        await last_message.set(sent_message, state)
        return

    await state.update_data(input_question_id=input_question_id)

    sent_message = await send_enter_question_text(
        message,
        SendAction.ANSWER,
        PARENT_DIR,
    )
    await last_message.set(sent_message, state)

    await state.set_state(FormulationCreation.waiting_for_question_text)


@router.message(FormulationCreation.waiting_for_question_text)
async def formulation_create_msg_question_text_handler(
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

    data = await state.get_data()
    if is_expired(data):
        await state.clear()
        return await send_expired(
            message,
            SendAction.ANSWER,
            PARENT_DIR,
        )
    await state.set_data(data)

    input_question_id: int = data["input_question_id"]

    await send_confirm_creation(
        message,
        SendAction.ANSWER,
        input_question_id,
        input_question_text,
    )

    await state.set_state(None)


@router.callback_query(ConfirmCallback.filter(F.dir == DIR))
async def formulation_create_cb_confirm_handler(
    callback: CallbackQuery,
    state: TempContext,
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

    input_question_id: int = data["input_question_id"]
    input_question_text: str = data["input_question_text"]

    try:
        formulation = await formulation_gateway.create_formulation(
            input_question_id,
            input_question_text,
        )
    except NotFoundError as exc:
        await state.clear()
        return await send_invalid(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.ANSWER,
            PARENT_DIR,
            str(exc),
        )
    except BadGatewayError:
        await state.clear()
        return await send_embedding_failed(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.ANSWER,
            PARENT_DIR,
        )

    await state.clear()

    logger.debug("Formulation created", id=formulation.id)
    await send_successfully_created(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        formulation.id,
        formulation.question_id,
        formulation.question_text,
    )
