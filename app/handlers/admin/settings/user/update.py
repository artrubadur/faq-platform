from aiogram import Bot, Dispatcher, F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger
from sqlalchemy.exc import IntegrityError, NoResultFound

from app.core.constants.dirs import USERS_UPDATE
from app.dialogs import SendAction
from app.dialogs.rows.common import (
    BackCallback,
    CancelCallback,
    ConfirmCallback,
    EditCallback,
    SaveCallback,
)
from app.dialogs.rows.user import IdentityCallback, RoleCallback, UsernameCallback
from app.dialogs.send.admin.user import (
    send_already_exists,
    send_changes,
    send_confirm_update,
    send_enter_identity,
    send_enter_username,
    send_not_found,
    send_select_role,
    send_successfully_updated,
)
from app.dialogs.send.common import send_expired, send_invalid
from app.repositories import UsersRepository
from app.services import UsersService
from app.services.user.process import (
    process_identity_msg,
    process_role_msg,
    process_username_msg,
)
from app.storage.core import async_session
from app.storage.temp import TempContext
from app.utils.history.last_message import LastMessage
from app.utils.state import is_expired, update_data

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

    await state.update_data({"in_operation": True})
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
        async with async_session() as session:
            repo = UsersRepository(session)
            service = UsersService(repo)
            user = await service.get_user(input_id)
    except NoResultFound:
        await state.clear()
        await send_not_found(message, send_action, input_id, input_username)
        return

    await state.update_data(
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
    except ValueError as e:
        sent_message = await send_invalid(
            message, SendAction.ANSWER, PARENT_DIR, str(e)
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
    if is_expired(data):
        await state.clear()
        await send_expired(
            message,
            SendAction.ANSWER,
            PARENT_DIR,
        )
        return

    id: int = data["orig_id"]
    username: str | None = data["orig_username"]
    role: str = data["orig_role"]

    edited_username: str | None = data.get("edited_username", username)
    edited_role: str = data.get("edited_role", role)

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
    except ValueError as e:
        sent_message = await send_invalid(message, SendAction.ANSWER, DIR, str(e))
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
    except ValueError as e:
        sent_message = await send_invalid(message, SendAction.ANSWER, DIR, str(e))
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
    if is_expired(data):
        await state.clear()
        await send_expired(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.ANSWER,
            PARENT_DIR,
        )
        return

    id: int = data["orig_id"]
    username: str | None = data["orig_username"]
    role: str = data["orig_role"]

    edited_username: str | None = data.get("edited_username", username)
    edited_role: str = data.get("edited_role", role)

    try:
        async with async_session() as session:
            repo = UsersRepository(session)
            service = UsersService(repo)
            user = await service.update_user(
                id, username=edited_username, role=edited_role
            )
    except NoResultFound:
        await state.clear()
        await send_not_found(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.EDIT,
            id,
            username,
        )
        return
    except IntegrityError:
        await state.clear()
        await send_already_exists(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.EDIT,
            user.telegram_id,
            user.username,
        )
        return

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
