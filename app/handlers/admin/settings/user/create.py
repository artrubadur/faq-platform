from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger
from sqlalchemy.exc import IntegrityError

from app.core.constants.dirs import USERS_CREATE
from app.dialogs import SendAction
from app.dialogs.rows.common import ConfirmCallback
from app.dialogs.rows.user import IdentityCallback, RoleCallback, UsernameCallback
from app.dialogs.send.admin.user import (
    send_confirm_creation,
    send_enter_identity,
    send_enter_username,
    send_failed_creation,
    send_select_role,
    send_successfully_created,
)
from app.dialogs.send.common import send_invalid
from app.repositories import UsersRepository
from app.services import UsersService
from app.services.user.process import (
    process_identity_msg,
    process_role_msg,
    process_username_msg,
)
from app.storage.core import async_session
from app.utils.history.last_message import LastMessage

router = Router()

PARENT_DIR, DIR = USERS_CREATE


class UserCreation(StatesGroup):
    waiting_for_identity = State()
    waiting_for_username = State()
    waiting_for_role = State()


@router.callback_query(F.data == DIR)
async def user_create_cb_handler(
    callback: CallbackQuery, last_message: LastMessage, state: FSMContext
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    found_user_id: int | None = data.get("glb_found_user_id", None)
    found_username = data.get("glb_found_username", None)

    sent_message = await send_enter_identity(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        PARENT_DIR,
        DIR,
        found_user_id,
        found_username,
    )
    await last_message.set(sent_message, state)

    await state.set_state(UserCreation.waiting_for_identity)


async def process_identity_handler(
    message: Message,
    last_message: LastMessage,
    state: FSMContext,
    input_id: int,
    input_username: str | None,
    *,
    send_action: SendAction,
):
    await state.update_data(tmp_input_id=input_id, tmp_input_username=input_username)

    if input_username is None:
        data = await state.get_data()
        found_username = data.get("glb_found_username", None)

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
    message: Message, last_message: LastMessage, state: FSMContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_id, input_username = await process_identity_msg(message)
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
    state: FSMContext,
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
    state: FSMContext,
    input_username: str | None,
    *,
    send_action: SendAction,
):
    await state.update_data(tmp_input_username=input_username)

    sent_message = await send_select_role(message, send_action, PARENT_DIR, DIR)
    await last_message.set(sent_message, state)

    await state.set_state(UserCreation.waiting_for_role)


@router.message(UserCreation.waiting_for_username)
async def user_create_msg_username_handler(
    message: Message, last_message: LastMessage, state: FSMContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_username = await process_username_msg(message)
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
    state: FSMContext,
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
    state: FSMContext,
    input_role: str,
    *,
    send_action: SendAction,
):
    await state.update_data(tmp_input_role=input_role)

    data = await state.get_data()
    input_id: int = data["tmp_input_id"]
    input_username: str | None = data["tmp_input_username"]

    sent_message = await send_confirm_creation(
        message, send_action, input_id, input_username, input_role
    )
    await last_message.set(sent_message, state)

    await state.set_state(None)


@router.message(UserCreation.waiting_for_role)
async def user_create_msg_role_handler(
    message: Message, last_message: LastMessage, state: FSMContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_role = await process_role_msg(message)
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
    state: FSMContext,
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
async def user_create_cb_confirm_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    input_id: int = data.pop("tmp_input_id")
    input_username: str | None = data.pop("tmp_input_username")
    input_role: str = data.pop("tmp_input_role")
    await state.set_data(data)

    async with async_session() as session:
        repo = UsersRepository(session)
        service = UsersService(repo)
        try:
            user = await service.create_user(input_id, input_username, input_role)
            logger.debug("User created", id=user.id)
            await send_successfully_created(
                callback.message,  # pyright: ignore[reportArgumentType]
                SendAction.EDIT,
                user.telegram_id,
                user.username,
                user.role,
            )
        except IntegrityError:
            await send_failed_creation(
                callback.message,  # pyright: ignore[reportArgumentType]
                SendAction.EDIT,
                "User already exists",
            )
