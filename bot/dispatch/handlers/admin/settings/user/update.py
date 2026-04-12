from aiogram import Bot, Dispatcher, F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger

from bot.core.dirs import USERS_UPDATE
from bot.dialogs import SendAction
from bot.dialogs.rows.common import (
    BackCallback,
    CancelCallback,
    ConfirmCallback,
    EditCallback,
    SaveCallback,
)
from bot.dialogs.rows.user import IdentityCallback, RoleCallback, UsernameCallback
from bot.dialogs.send.admin.user import (
    send_already_exists,
    send_changes,
    send_confirm_update,
    send_enter_identity,
    send_enter_username,
    send_not_found,
    send_select_role,
    send_successfully_updated,
)
from bot.dialogs.send.common import send_access_denied, send_expired, send_invalid
from bot.services.user.gateway import user_gateway
from bot.services.user.process import (
    process_identity_msg,
    process_role_msg,
    process_username_msg,
)
from bot.utils.state.data import update_data
from bot.utils.state.history import LastMessage
from bot.utils.state.operation import (
    extend_operation,
    is_operation_expired,
    start_operation,
)
from bot.utils.state.temp import TempContext
from shared.api.exceptions import ConflictError, ForbiddenError, NotFoundError
from shared.contracts.user.responses import Role

router = Router()

PARENT_DIR, DIR = USERS_UPDATE


class UserUpdate(StatesGroup):
    waiting_for_identity = State()
    waiting_for_username = State()
    waiting_for_role = State()


@router.callback_query(F.data == DIR)
async def user_update_cb_handler(
    callback: CallbackQuery, last_message: LastMessage, state: TempContext
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.storage.get_data(state.key, "long")
    found_user_id: int | None = data.get("found_user_id", None)
    found_username: str | None = data.get("found_username", None)

    sent_message = await send_enter_identity(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        PARENT_DIR,
        DIR,
        found_user_id,
        found_username,
    )
    await last_message.set(sent_message, state)

    await state.set_state(UserUpdate.waiting_for_identity)


async def process_identity_handler(
    message: Message,
    state: TempContext,
    input_id: int,
    input_username: str | None,
    *,
    send_action: SendAction,
):
    try:
        user = await user_gateway.get_user(input_id)
    except NotFoundError:
        await state.clear()
        return await send_not_found(message, send_action, input_id, input_username)

    await start_operation(
        state,
        orig_id=user.telegram_id,
        orig_username=user.username,
        orig_role=user.role,
    )
    await send_confirm_update(
        message,
        send_action,
        user.telegram_id,
        user.username,
        user.role,
    )
    await state.set_state(None)


@router.message(UserUpdate.waiting_for_identity)
async def user_update_msg_identity_handler(
    message: Message, last_message: LastMessage, state: TempContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_id, input_username = process_identity_msg(message)
    except ValueError as exc:
        sent_message = await send_invalid(
            message, SendAction.ANSWER, PARENT_DIR, str(exc)
        )
        await last_message.set(sent_message, state)
        return

    await process_identity_handler(
        message, state, input_id, input_username, send_action=SendAction.ANSWER
    )


@router.callback_query(IdentityCallback.filter(F.dir == DIR))
async def user_update_cb_identity_handler(
    callback: CallbackQuery, callback_data: IdentityCallback, state: TempContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    input_id = callback_data.id
    input_username = callback_data.username

    await process_identity_handler(
        callback.message,  # pyright: ignore[reportArgumentType]
        state,
        input_id,
        input_username,
        send_action=SendAction.EDIT,
    )


async def process_fields_handler(
    message: Message, state: TempContext, *, send_action: SendAction
):
    data = await state.get_data()
    if is_operation_expired(data):
        await state.clear()
        return await send_expired(
            message,
            SendAction.ANSWER,
            PARENT_DIR,
        )
    await extend_operation(state)

    id: int = data["orig_id"]
    username: str | None = data["orig_username"]
    role: Role = Role(data["orig_role"])

    edited_username: str | None = data.get("edited_username", username)
    edited_role: Role = Role(data.get("edited_role", role))

    await send_changes(
        message,
        send_action,
        id,
        username,
        edited_username,
        role,
        edited_role,
    )

    await state.set_state(None)


@router.callback_query(ConfirmCallback.filter(F.dir == DIR))
async def user_update_confirm_cb_fields_handler(
    callback: CallbackQuery, state: TempContext
):
    await callback.answer()
    await process_fields_handler(
        callback.message,  # pyright: ignore[reportArgumentType]
        state,
        send_action=SendAction.EDIT,
    )


@router.callback_query(CancelCallback.filter(F.dir == DIR))
async def user_update_cancel_cb_fields_handler(
    callback: CallbackQuery, state: TempContext
):
    await callback.answer()
    await process_fields_handler(
        callback.message,  # pyright: ignore[reportArgumentType]
        state,
        send_action=SendAction.EDIT,
    )


@router.callback_query(BackCallback.filter(F.dir == DIR))
async def user_update_back_cb_fields_handler(
    callback: CallbackQuery, state: TempContext
):
    await callback.answer()
    await process_fields_handler(
        callback.message,  # pyright: ignore[reportArgumentType]
        state,
        send_action=SendAction.EDIT,
    )


@router.callback_query(EditCallback.filter((F.dir == DIR) & (F.field == "username")))
async def user_update_cb_edit_username_handler(
    callback: CallbackQuery, last_message: LastMessage, state: TempContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    found_username: str | None = await state.storage.get_value(
        state.key, "found_username", None, "long"
    )

    sent_message = await send_enter_username(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        DIR,
        DIR,
        found_username,
    )
    await last_message.set(sent_message, state)

    await state.set_state(UserUpdate.waiting_for_username)


@router.message(UserUpdate.waiting_for_username)
async def user_update_msg_edited_username_handler(
    message: Message, last_message: LastMessage, state: TempContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_username = process_username_msg(message)
    except ValueError as exc:
        sent_message = await send_invalid(message, SendAction.ANSWER, DIR, str(exc))
        await last_message.set(sent_message, state)
        return

    await state.update_data(edited_username=input_username)

    await process_fields_handler(message, state, send_action=SendAction.ANSWER)


@router.callback_query(UsernameCallback.filter(F.dir == DIR))
async def user_update_cb_edited_username_handler(
    callback: CallbackQuery, callback_data: UsernameCallback, state: TempContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    input_username = callback_data.username
    await state.update_data(edited_username=input_username)

    await process_fields_handler(
        callback.message,  # pyright: ignore[reportArgumentType]
        state,
        send_action=SendAction.EDIT,
    )


@router.callback_query(EditCallback.filter((F.dir == DIR) & (F.field == "role")))
async def user_update_msg_edit_role_handler(
    callback: CallbackQuery, last_message: LastMessage, state: TempContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    sent_message = await send_select_role(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        DIR,
        DIR,
    )
    await last_message.set(sent_message, state)

    await state.set_state(UserUpdate.waiting_for_role)


@router.message(UserUpdate.waiting_for_role)
async def user_update_msg_edited_role_handler(
    message: Message, last_message: LastMessage, state: TempContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_role = process_role_msg(message)
    except ValueError as exc:
        sent_message = await send_invalid(message, SendAction.ANSWER, DIR, str(exc))
        await last_message.set(sent_message, state)
        return

    await state.update_data(edited_role=input_role)

    await process_fields_handler(message, state, send_action=SendAction.ANSWER)


@router.callback_query(RoleCallback.filter(F.dir == DIR))
async def user_update_cb_edited_role_handler(
    callback: CallbackQuery, callback_data: RoleCallback, state: TempContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    input_role = callback_data.role
    await state.update_data(edited_role=input_role)

    await process_fields_handler(
        callback.message,  # pyright: ignore[reportArgumentType]
        state,
        send_action=SendAction.EDIT,
    )


@router.callback_query(SaveCallback.filter(F.dir == DIR))
async def user_update_cb_save_handler(
    callback: CallbackQuery,
    state: TempContext,
    bot: Bot,
    dispatcher: Dispatcher,
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

    id: int = data["orig_id"]
    username: str | None = data["orig_username"]
    role: Role = Role(data["orig_role"])

    edited_username: str | None = data.get("edited_username", username)
    edited_role: Role = Role(data.get("edited_role", role))

    try:
        user = await user_gateway.update_user(id, edited_role, edited_username)
    except NotFoundError:
        await state.clear()
        return await send_not_found(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.EDIT,
            id,
            username,
        )
    except ConflictError:
        await state.clear()
        return await send_already_exists(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.EDIT,
            id,
            username,
        )
    except ForbiddenError as exc:
        await state.clear()
        return await send_access_denied(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.EDIT,
            PARENT_DIR,
            str(exc),
        )

    if role != edited_role:
        await update_data(bot, dispatcher, id, {"sender_role": edited_role}, "long")

    await state.clear()

    logger.debug("User updated", id=user.id)
    await send_successfully_updated(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        user.telegram_id,
        user.username,
        user.role,
    )
