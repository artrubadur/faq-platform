# pyright: reportArgumentType=false
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.exc import IntegrityError, NoResultFound

from app.dialogs import SendAction
from app.dialogs.rows.base import (
    BackCallback,
    CancelCallback,
    ConfirmCallback,
    EditCallback,
    SaveCallback,
)
from app.dialogs.rows.user import IdentityCallback, RoleCallback, UsernameCallback
from app.dialogs.send.user import (
    send_changes,
    send_confirm_update,
    send_edit_role,
    send_edit_username,
    send_enter_identity,
    send_failed_update,
    send_invalid,
    send_not_found,
    send_successfully_updated,
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
DIR = "settings.users.update"


class Update(StatesGroup):
    waiting_for_identity = State()
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
    await state.set_state(Update.waiting_for_identity)


# Confirm
async def process_identity_confirm_handler(
    message: Message,
    state: FSMContext,
    input_id: int,
    input_username: str | None,
    *,
    send_action: SendAction
):
    async with async_session() as session:
        repo = UsersRepository(session)
        service = UsersService(repo)
        try:
            user = await service.read_user(input_id)
            await state.update_data(
                orig_id=user.telegram_id,
                orig_username=user.username,
                orig_role=user.role.value,
            )
            await send_confirm_update(
                message,
                user.telegram_id,
                user.username,
                user.role.value,
                action=send_action,
            )
        except NoResultFound:
            await send_not_found(message, input_id, input_username, action=send_action)

    await state.set_state(None)


@router.message(Update.waiting_for_identity)
async def msg_identity_confirm_handler(message: Message, state: FSMContext):
    try:
        input_id, input_username = await process_identity_msg(message)
    except ValueError as e:
        await send_invalid(message, PARENT_DIR, str(e), action=SendAction.ANSWER)
        return

    await process_identity_confirm_handler(
        message, state, input_id, input_username, send_action=SendAction.ANSWER
    )


@router.callback_query(IdentityCallback.filter(F.dir == DIR))
async def cb_identity_confirm_handler(
    callback: CallbackQuery, callback_data: IdentityCallback, state: FSMContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    input_id = callback_data.id
    input_username = callback_data.username

    await process_identity_confirm_handler(
        callback.message, state, input_id, input_username, send_action=SendAction.EDIT
    )


# Field
async def process_field_edit_handler(
    message: Message, state: FSMContext, *, send_action: SendAction
):
    data = await state.get_data()
    id: int = data["orig_id"]
    username: str | None = data["orig_username"]
    role: str = data["orig_role"]

    edited_id: int = data.get("edited_id", id)
    edited_username: str | None = data.get("edited_username", username)
    edited_role: str = data.get("edited_role", role)

    await send_changes(
        message,
        id,
        edited_id,
        username,
        edited_username,
        role,
        edited_role,
        action=send_action,
    )


@router.callback_query(ConfirmCallback.filter(F.dir == DIR))
async def cb_confirm_field_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await process_field_edit_handler(
        callback.message, state, send_action=SendAction.EDIT
    )


@router.callback_query(CancelCallback.filter(F.dir == DIR))
async def cb_cancel_field_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await process_field_edit_handler(
        callback.message, state, send_action=SendAction.EDIT
    )


@router.callback_query(BackCallback.filter(F.dir == DIR))
async def cb_back_field_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await process_field_edit_handler(
        callback.message, state, send_action=SendAction.EDIT
    )


# Edit
# Username
@router.callback_query(EditCallback.filter(F.dir == DIR and F.field == "username"))
async def cb_edit_username_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    found_username = data.get("found_username", None)

    await send_edit_username(
        callback.message, DIR, found_username, action=SendAction.EDIT
    )
    await state.set_state(Update.waiting_for_username)


@router.message(Update.waiting_for_username)
async def msg_username_edited_handler(message: Message, state: FSMContext):
    try:
        input_username = await process_username_msg(message)
    except ValueError as e:
        await send_invalid(message, DIR, str(e), action=SendAction.ANSWER)
        return

    await state.update_data(edited_username=input_username)

    await process_field_edit_handler(message, state, send_action=SendAction.ANSWER)


@router.callback_query(UsernameCallback.filter(F.dir == DIR))
async def cb_username_edited_handler(
    callback: CallbackQuery, callback_data: UsernameCallback, state: FSMContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    input_username = callback_data.username

    await state.update_data(edited_username=input_username)
    await process_field_edit_handler(
        callback.message, state, send_action=SendAction.EDIT
    )


# Role
@router.callback_query(EditCallback.filter(F.dir == DIR and F.field == "role"))
async def cb_edit_role_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    await send_edit_role(callback.message, DIR, action=SendAction.EDIT)
    await state.set_state(Update.waiting_for_role)


@router.message(Update.waiting_for_role)
async def msg_role_edited_handler(message: Message, state: FSMContext):
    try:
        input_role = await process_role_msg(message)
    except ValueError as e:
        await send_invalid(message, DIR, str(e), action=SendAction.ANSWER)
        return

    await state.update_data(edited_role=input_role)

    await process_field_edit_handler(message, state, send_action=SendAction.ANSWER)


@router.callback_query(RoleCallback.filter(F.dir == DIR))
async def cb_role_edited_handler(
    callback: CallbackQuery, callback_data: RoleCallback, state: FSMContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    input_role = callback_data.role

    await state.update_data(edited_role=input_role)
    await process_field_edit_handler(
        callback.message, state, send_action=SendAction.EDIT
    )


# Save
@router.callback_query(SaveCallback.filter(F.dir == DIR))
async def cb_edit_save_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    id: int = data.pop("orig_id")
    username: str | None = data.pop("orig_username")
    role: str = data.pop("orig_role")

    edited_username: str | None = data.pop("edited_username", username)
    edited_role: str = data.pop("edited_role", role)

    await state.update_data(input_id=None, input_username=None, input_role=None)

    async with async_session() as session:
        repo = UsersRepository(session)
        service = UsersService(repo)
        try:
            user = await service.update_user(id, edited_username, edited_role)
            await send_successfully_updated(
                callback.message,
                user.telegram_id,
                user.username,
                user.role,
                action=SendAction.EDIT,
            )
        except NoResultFound:
            await send_not_found(callback.message, id, username, action=SendAction.EDIT)
        except IntegrityError:
            await send_failed_update(
                callback.message, "Username already claimed.", action=SendAction.EDIT
            )
