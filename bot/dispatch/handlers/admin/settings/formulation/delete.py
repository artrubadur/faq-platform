from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger

from bot.core.dirs import FORMULATIONS_DELETE
from bot.dialogs import SendAction
from bot.dialogs.rows.common import ConfirmCallback
from bot.dialogs.rows.formulation import IdCallback
from bot.dialogs.send.admin.formulation import (
    send_confirm_deletion,
    send_enter_id,
    send_not_found,
    send_successfully_deleted,
)
from bot.dialogs.send.common import send_expired, send_invalid
from bot.services.formulation.gateway import formulation_gateway
from bot.services.formulation.process import process_id_msg
from bot.utils.state.history import LastMessage
from bot.utils.state.operation import is_operation_expired, start_operation
from bot.utils.state.temp import TempContext
from shared.api.exceptions import NotFoundError

router = Router()

PARENT_DIR, DIR = FORMULATIONS_DELETE


class FormulationDeletion(StatesGroup):
    waiting_for_id = State()


@router.callback_query(F.data == DIR)
async def formulation_delete_cb_handler(
    callback: CallbackQuery, last_message: LastMessage, state: TempContext
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    found_formulation_id: int | None = await state.storage.get_value(
        state.key,
        "found_formulation_id",
        None,
        "long",
    )

    sent_message = await send_enter_id(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        PARENT_DIR,
        DIR,
        found_formulation_id,
    )
    await last_message.set(sent_message, state)

    await state.set_state(FormulationDeletion.waiting_for_id)


async def process_id_handler(
    message: Message, state: TempContext, input_id: int, *, send_action: SendAction
):
    try:
        formulation = await formulation_gateway.get_formulation(input_id)
    except NotFoundError:
        await send_not_found(message, send_action, input_id)
        await state.set_state(None)
        return

    await start_operation(state, input_id=input_id)

    await send_confirm_deletion(
        message,
        send_action,
        formulation.id,
        formulation.question_id,
        formulation.question_text,
    )
    await state.set_state(None)


@router.message(FormulationDeletion.waiting_for_id)
async def formulation_delete_msg_id_handler(
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
async def formulation_delete_cb_id_handler(
    callback: CallbackQuery,
    callback_data: IdCallback,
    state: TempContext,
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


@router.callback_query(ConfirmCallback.filter(F.dir == DIR))
async def formulation_delete_cb_confirm_handler(
    callback: CallbackQuery,
    state: TempContext,
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    if is_operation_expired(data):
        await state.clear()
        return await send_expired(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.ANSWER,
            PARENT_DIR,
        )

    input_id: int = data["input_id"]

    try:
        formulation = await formulation_gateway.delete_formulation(input_id)
    except NotFoundError:
        await state.clear()
        return await send_not_found(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.EDIT,
            input_id,
        )

    await state.clear()

    logger.debug("Formulation deleted", id=formulation.id)
    await send_successfully_deleted(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        formulation.id,
        formulation.question_id,
        formulation.question_text,
    )
