from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger
from sqlalchemy.exc import IntegrityError

from app.bot.storage import LSTContext
from app.core.constants.dirs import USERS_CREATE
from app.dialogs import SendAction
from app.dialogs.rows.common import ConfirmCallback
from app.dialogs.rows.user import IdentityCallback, RoleCallback, UsernameCallback
from app.dialogs.send.admin.user import (
    send_already_exists,
    send_confirm_creation,
    send_enter_identity,
    send_enter_username,
    send_select_role,
    send_successfully_created,
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
from app.utils.history.last_message import LastMessage
from app.utils.state import is_expired

router = Router()

PARENT_DIR, DIR = USERS_CREATE


class UserCreation(StatesGroup):
    waiting_for_identity = State()
    waiting_for_username = State()
    waiting_for_role = State()


@router.callback_query(F.data == DIR)
async def user_create_cb_handler(
    callback: CallbackQuery, last_message: LastMessage, state: LSTContext
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

    await state.update_data(in_operation=True)
    await state.set_state(UserCreation.waiting_for_identity)


async def process_identity_handler(
    message: Message,
    last_message: LastMessage,
    state: LSTContext,
    input_id: int,
    input_username: str | None,
    *,
    send_action: SendAction,
):
    await state.update_data(input_id=input_id, input_username=input_username)

    if input_username is None:
        data = await state.get_data()
        found_username = data.get("found_username", None)

        sent_message = await send_enter_username(
            message, send_action, PARENT_DIR, DIR, found_username
        )
        await last_message.set(sent_message, state)

        await state.set_state(UserCreation.waiting_for_username)
    else:
        sent_message = await send_select_role(message, send_action, PARENT_DIR, DIR)
        await last_message.set(sent_message, state)

        await state.set_state(UserCreation.waiting_for_role)


@router.message(UserCreation.waiting_for_identity)
async def user_create_msg_identity_handler(
    message: Message, last_message: LastMessage, state: LSTContext
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
        message,
        last_message,
        state,
        input_id,
        input_username,
        send_action=SendAction.ANSWER,
    )


@router.callback_query(IdentityCallback.filter(F.dir == DIR))
async def user_create_cb_identity_handler(
    callback: CallbackQuery,
    last_message: LastMessage,
    callback_data: IdentityCallback,
    state: LSTContext,
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    input_id = callback_data.id
    input_username = callback_data.username

    await process_identity_handler(
        callback.message,  # pyright: ignore[reportArgumentType]
        last_message,
        state,
        input_id,
        input_username,
        send_action=SendAction.EDIT,
    )


async def process_username_handler(
    message: Message,
    last_message: LastMessage,
    state: LSTContext,
    input_username: str | None,
    *,
    send_action: SendAction,
):
    await state.update_data(input_username=input_username)

    sent_message = await send_select_role(message, send_action, PARENT_DIR, DIR)
    await last_message.set(sent_message, state)

    await state.set_state(UserCreation.waiting_for_role)


@router.message(UserCreation.waiting_for_username)
async def user_create_msg_username_handler(
    message: Message, last_message: LastMessage, state: LSTContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_username = process_username_msg(message)
    except ValueError as e:
        sent_message = await send_invalid(
            message, SendAction.ANSWER, PARENT_DIR, str(e)
        )
        await last_message.set(sent_message, state)
        return

    await process_username_handler(
        message, last_message, state, input_username, send_action=SendAction.ANSWER
    )


@router.callback_query(UsernameCallback.filter(F.dir == DIR))
async def user_create_cb_username_handler(
    callback: CallbackQuery,
    last_message: LastMessage,
    callback_data: UsernameCallback,
    state: LSTContext,
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    input_username = callback_data.username

    await process_username_handler(
        callback.message,  # pyright: ignore[reportArgumentType]
        last_message,
        state,
        input_username,
        send_action=SendAction.EDIT,
    )


async def process_role_handler(
    message: Message,
    last_message: LastMessage,
    state: LSTContext,
    input_role: str,
    *,
    send_action: SendAction,
):
    await state.update_data(input_role=input_role)

    data = await state.get_data()
    if is_expired(data):
        await state.clear()
        await send_expired(
            message,
            SendAction.ANSWER,
            PARENT_DIR,
        )
        return

    input_id: int = data["input_id"]
    input_username: str | None = data["input_username"]

    sent_message = await send_confirm_creation(
        message, send_action, input_id, input_username, input_role
    )
    await last_message.set(sent_message, state)

    await state.set_state(None)


@router.message(UserCreation.waiting_for_role)
async def user_create_msg_role_handler(
    message: Message, last_message: LastMessage, state: LSTContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_role = process_role_msg(message)
    except ValueError as e:
        sent_message = await send_invalid(
            message, SendAction.ANSWER, PARENT_DIR, str(e)
        )
        await last_message.set(sent_message, state)
        return

    await process_role_handler(
        message, last_message, state, input_role, send_action=SendAction.ANSWER
    )


@router.callback_query(RoleCallback.filter(F.dir == DIR))
async def user_create_cb_role_handler(
    callback: CallbackQuery,
    last_message: LastMessage,
    callback_data: RoleCallback,
    state: LSTContext,
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    input_role = callback_data.role

    await process_role_handler(
        callback.message,  # pyright: ignore[reportArgumentType]
        last_message,
        state,
        input_role,
        send_action=SendAction.EDIT,
    )


@router.callback_query(ConfirmCallback.filter(F.dir == DIR))
async def user_create_cb_confirm_handler(callback: CallbackQuery, state: LSTContext):
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

    input_id: int = data["input_id"]
    input_username: str | None = data["input_username"]
    input_role: str = data["input_role"]

    try:
        async with async_session() as session:
            repo = UsersRepository(session)
            service = UsersService(repo)
            user = await service.create_user(input_id, input_username, input_role)
    except IntegrityError:
        await state.clear()
        await send_already_exists(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.EDIT,
            input_id,
            input_username,
        )
        return

    await state.clear()

    logger.debug("User created", id=user.id)
    await send_successfully_created(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        user.telegram_id,
        user.username,
        user.role,
    )
