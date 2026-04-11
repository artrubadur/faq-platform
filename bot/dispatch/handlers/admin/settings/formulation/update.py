from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger

from bot.core.dirs import FORMULATIONS_UPDATE
from bot.dialogs import SendAction
from bot.dialogs.rows.common import (
    BackCallback,
    CancelCallback,
    ConfirmCallback,
    EditCallback,
    SaveCallback,
)
from bot.dialogs.rows.formulation import IdCallback
from bot.dialogs.send.admin.formulation import (
    send_changes,
    send_confirm_recompute,
    send_confirm_update,
    send_embedding_failed,
    send_enter_id,
    send_enter_question_id,
    send_enter_question_text,
    send_not_found,
    send_successfully_updated,
)
from bot.dialogs.send.common import send_expired, send_invalid
from bot.services.formulation.gateway import formulation_gateway
from bot.services.formulation.process import (
    process_id_msg,
    process_question_id_msg,
    process_question_text_msg,
)
from bot.utils.state.history import LastMessage, is_expired
from bot.utils.state.temp import TempContext
from shared.api.exceptions import BadGatewayError, NotFoundError
from shared.contracts.formulation.requests import UpdateFormulationRequest

router = Router()

PARENT_DIR, DIR = FORMULATIONS_UPDATE


class FormulationUpdate(StatesGroup):
    waiting_for_id = State()
    waiting_for_question_text = State()
    waiting_for_question_id = State()


@router.callback_query(F.data == DIR)
async def formulation_update_cb_handler(
    callback: CallbackQuery, last_message: LastMessage, state: TempContext
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    found_formulation_id: int | None = await state.storage.get_value(
        state.key, "found_formulation_id", None, "long"
    )

    sent_message = await send_enter_id(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        PARENT_DIR,
        DIR,
        found_formulation_id,
    )
    await last_message.set(sent_message, state)

    await state.set_data({"in_operation": True})
    await state.set_state(FormulationUpdate.waiting_for_id)


async def process_id_handler(
    message: Message, state: TempContext, input_id: int, *, send_action: SendAction
):
    try:
        formulation = await formulation_gateway.get_formulation(input_id)
    except NotFoundError:
        await send_not_found(message, send_action, input_id)
        await state.set_state(None)
        return

    await state.update_data(
        orig_id=formulation.id,
        orig_question_id=formulation.question_id,
        orig_question_text=formulation.question_text,
        recompute_embedding=False,
    )
    await send_confirm_update(
        message,
        send_action,
        formulation.id,
        formulation.question_id,
        formulation.question_text,
    )

    await state.set_state(None)


@router.message(FormulationUpdate.waiting_for_id)
async def formulation_update_msg_id_handler(
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
async def formulation_update_cb_id_handler(
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
    question_id: int = data["orig_question_id"]
    question_text: str = data["orig_question_text"]

    edited_question_id: int = data.get("edited_question_id", question_id)
    edited_question_text: str = data.get("edited_question_text", question_text)
    recompute_embedding: bool = data.get("recompute_embedding", False)

    await send_changes(
        message,
        send_action,
        id,
        question_id,
        edited_question_id,
        question_text,
        edited_question_text,
        recompute_embedding,
    )


@router.callback_query(ConfirmCallback.filter((F.dir == DIR) & (F.step == "update")))
async def formulation_update_confirm_cb_fields_handler(
    callback: CallbackQuery,
    state: TempContext,
):
    await callback.answer()
    await process_fields_handler(
        callback.message,  # pyright: ignore[reportArgumentType]
        state,
        send_action=SendAction.EDIT,
    )


@router.callback_query(CancelCallback.filter(F.dir == PARENT_DIR))
async def formulation_update_cancel_cb_fields_handler(
    callback: CallbackQuery,
    state: TempContext,
):
    await callback.answer()
    await process_fields_handler(
        callback.message,  # pyright: ignore[reportArgumentType]
        state,
        send_action=SendAction.EDIT,
    )


@router.callback_query(BackCallback.filter(F.dir == DIR))
async def formulation_update_back_cb_fields_handler(
    callback: CallbackQuery,
    state: TempContext,
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
async def formulation_update_cb_edit_question_text_handler(
    callback: CallbackQuery,
    last_message: LastMessage,
    state: TempContext,
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    sent_message = await send_enter_question_text(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        DIR,
    )
    await last_message.set(sent_message, state)

    await state.set_state(FormulationUpdate.waiting_for_question_text)


@router.message(FormulationUpdate.waiting_for_question_text)
async def formulation_update_msg_edited_question_text_handler(
    message: Message,
    last_message: LastMessage,
    state: TempContext,
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_question_text = process_question_text_msg(message)
    except ValueError as exc:
        sent_message = await send_invalid(message, SendAction.ANSWER, DIR, str(exc))
        await last_message.set(sent_message, state)
        return

    data = await state.get_data()
    question_text: str = data["orig_question_text"]

    await state.update_data(edited_question_text=input_question_text)

    if question_text == input_question_text:
        await state.update_data(recompute_embedding=False)
        await process_fields_handler(message, state, send_action=SendAction.ANSWER)
        await state.set_state(None)
        return

    sent_message = await send_confirm_recompute(message, SendAction.ANSWER)
    await last_message.set(sent_message, state)

    await state.set_state(None)


@router.callback_query(ConfirmCallback.filter((F.dir == DIR) & (F.step == "recompute")))
async def formulation_update_cb_confirm_recompute_handler(
    callback: CallbackQuery,
    state: TempContext,
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    await state.update_data(recompute_embedding=True)

    await process_fields_handler(
        callback.message,  # pyright: ignore[reportArgumentType]
        state,
        send_action=SendAction.EDIT,
    )


@router.callback_query(CancelCallback.filter(F.dir == DIR))
async def formulation_update_cb_cancel_recompute_handler(
    callback: CallbackQuery,
    state: TempContext,
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    await state.update_data(recompute_embedding=False)

    await process_fields_handler(
        callback.message,  # pyright: ignore[reportArgumentType]
        state,
        send_action=SendAction.EDIT,
    )


@router.callback_query(EditCallback.filter((F.dir == DIR) & (F.field == "question_id")))
async def formulation_update_cb_edit_question_id_handler(
    callback: CallbackQuery,
    last_message: LastMessage,
    state: TempContext,
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    sent_message = await send_enter_question_id(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        DIR,
    )
    await last_message.set(sent_message, state)

    await state.set_state(FormulationUpdate.waiting_for_question_id)


@router.message(FormulationUpdate.waiting_for_question_id)
async def formulation_update_msg_edited_question_id_handler(
    message: Message,
    last_message: LastMessage,
    state: TempContext,
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_question_id = process_question_id_msg(message)
    except ValueError as exc:
        sent_message = await send_invalid(message, SendAction.ANSWER, DIR, str(exc))
        await last_message.set(sent_message, state)
        return

    await state.update_data(edited_question_id=input_question_id)

    await process_fields_handler(message, state, send_action=SendAction.ANSWER)

    await state.set_state(None)


@router.callback_query(SaveCallback.filter(F.dir == DIR))
async def formulation_update_cb_save_handler(
    callback: CallbackQuery,
    state: TempContext,
):
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

    edited_question_id: int | None = data.get("edited_question_id", None)
    edited_question_text: str | None = data.get("edited_question_text", None)
    recompute_embedding: bool | None = data.get("recompute_embedding", None)

    request = UpdateFormulationRequest(
        question_id=edited_question_id,
        question_text=edited_question_text,
        recompute_embedding=recompute_embedding,
    )

    try:
        formulation = await formulation_gateway.update_formulation(
            id,
            **request.model_dump(mode="json", exclude_none=True),
        )
    except NotFoundError as exc:
        if "Question" in str(exc):
            await send_invalid(
                callback.message,  # pyright: ignore[reportArgumentType]
                SendAction.ANSWER,
                DIR,
                str(exc),
            )
            return

        await state.clear()
        await send_not_found(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.EDIT,
            id,
        )
        return
    except BadGatewayError:
        await state.clear()
        return await send_embedding_failed(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.ANSWER,
            PARENT_DIR,
        )

    await state.clear()

    logger.debug("Formulation updated", id=formulation.id)
    await send_successfully_updated(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        formulation.id,
        formulation.question_id,
        formulation.question_text,
    )
