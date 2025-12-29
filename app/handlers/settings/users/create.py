# pyright: reportArgumentType=false
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.exc import IntegrityError

from app.dialogs import SendAction
from app.dialogs.rows.base import ConfirmCallback
from app.dialogs.rows.user import IdentityCallback, RoleCallback, UsernameCallback
from app.dialogs.send.user import (
    send_confirm_creation,
    send_enter_identity,
    send_enter_username,
    send_failed_creation,
    send_invalid,
    send_select_role,
    send_successfully_created,
)
from app.repositories import UsersRepository
from app.services import UsersService
from app.services.user.process import (
    process_identity_msg,
    process_role_msg,
    process_username_msg,
)
from app.storage.db.engine import async_session

router = Router()

PARENT_DIR = "settings.users"
DIR = "settings.users.create"


class Creation(StatesGroup):
    waiting_for_id = State()
    waiting_for_username = State()
    waiting_for_role = State()


# Entry Point
@router.callback_query(F.data == DIR)
async def cb_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    found_id: int | None = data.get("found_id", None)
    found_username = data.get("found_username", None)

    await send_enter_identity(
        callback.message,
        DIR,
        found_id,
        found_username,
        action=SendAction.EDIT,
    )
    await state.set_state(Creation.waiting_for_id)


# ID / Identity
async def process_id_handler(
    message: Message,
    state: FSMContext,
    input_id: int,
    input_username: str | None,
    *,
    send_action: SendAction
):
    await state.update_data(input_id=input_id, input_username=input_username)

    if input_username is None:
        data = await state.get_data()
        found_username = data.get("found_username", None)

        await send_enter_username(message, DIR, found_username, action=send_action)
        await state.set_state(Creation.waiting_for_username)
    else:
        await send_select_role(message, DIR, action=send_action)
        await state.set_state(Creation.waiting_for_role)


@router.message(Creation.waiting_for_id)
async def msg_id_handler(message: Message, state: FSMContext):
    try:
        input_id, input_username = await process_identity_msg(message)
    except ValueError as e:
        await send_invalid(message, PARENT_DIR, str(e), action=SendAction.ANSWER)
        return

    await process_id_handler(
        message, state, input_id, input_username, send_action=SendAction.ANSWER
    )


@router.callback_query(IdentityCallback.filter(F.dir == DIR))
async def cb_id_handler(
    callback: CallbackQuery, callback_data: IdentityCallback, state: FSMContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    input_id = callback_data.id
    input_username = callback_data.username

    await process_id_handler(
        callback.message, state, input_id, input_username, send_action=SendAction.EDIT
    )


# Username
async def process_username_handler(
    message: Message,
    state: FSMContext,
    input_username: str | None,
    *,
    send_action: SendAction
):
    await state.update_data(input_username=input_username)

    await send_select_role(message, DIR, action=send_action)
    await state.set_state(Creation.waiting_for_role)


@router.message(Creation.waiting_for_username)
async def msg_username_handler(message: Message, state: FSMContext):
    try:
        input_username = await process_username_msg(message)
    except ValueError as e:
        await send_invalid(message, PARENT_DIR, str(e), action=SendAction.ANSWER)
        return

    await process_username_handler(
        message, state, input_username, send_action=SendAction.ANSWER
    )


@router.callback_query(UsernameCallback.filter(F.dir == DIR))
async def cb_username_handler(
    callback: CallbackQuery, callback_data: UsernameCallback, state: FSMContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    input_username = callback_data.username

    await process_username_handler(
        callback.message, state, input_username, send_action=SendAction.EDIT
    )


# Role
async def process_role_handler(
    message: Message, state: FSMContext, input_role: str, *, send_action: SendAction
):
    await state.update_data(input_role=input_role)
    data = await state.get_data()
    input_id: int = data["input_id"]
    input_username: str | None = data["input_username"]

    await send_confirm_creation(
        message, input_id, input_username, input_role, action=send_action
    )
    await state.set_state(None)


@router.message(Creation.waiting_for_role)
async def msg_confirm_handler(message: Message, state: FSMContext):
    try:
        input_role = await process_role_msg(message)
    except ValueError as e:
        await send_invalid(message, PARENT_DIR, str(e), action=SendAction.ANSWER)
        return

    await process_role_handler(
        message, state, input_role, send_action=SendAction.ANSWER
    )


@router.callback_query(RoleCallback.filter(F.dir == DIR))
async def cb_confirm_handler(
    callback: CallbackQuery, callback_data: RoleCallback, state: FSMContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    input_role = callback_data.role

    await process_role_handler(
        callback.message, state, input_role, send_action=SendAction.EDIT
    )


# Confirmation
@router.callback_query(ConfirmCallback.filter(F.dir == DIR))
async def cb_result_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    input_id: int = data["input_id"]
    input_username: str | None = data["input_username"]
    input_role: str = data["input_role"]

    await state.update_data(input_id=None, input_username=None, input_role=None)

    async with async_session() as session:
        repo = UsersRepository(session)
        service = UsersService(repo)
        try:
            user = await service.create_user(input_id, input_username, input_role)
            await send_successfully_created(
                callback.message,
                user.telegram_id,
                user.username,
                user.role,
                action=SendAction.EDIT,
            )
        except IntegrityError:
            await send_failed_creation(
                callback.message, "User already exists.", action=SendAction.EDIT
            )
