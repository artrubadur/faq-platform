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
from app.dialogs.send.base import send_invalid
from app.dialogs.send.user import (
    send_changes,
    send_confirm_update,
    send_edit_role,
    send_edit_username,
    send_enter_identity,
    send_failed_update,
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
from app.utils.history.last_message import LastMessage

from .root import DIR as PARENT_DIR

router = Router()

DIR = f"{PARENT_DIR}.update"


class Update(StatesGroup):
    waiting_for_identity = State()
    waiting_for_username = State()
    waiting_for_role = State()


@router.callback_query(F.data == DIR)
async def user_update_cb_handler(
    callback: CallbackQuery, last_message: LastMessage, state: FSMContext
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    found_user_id: int | None = data.get("found_user_id", None)
    found_username = data.get("found_username", None)

    sent_message = await send_enter_identity(
        callback.message,
        SendAction.EDIT,
        DIR,
        found_user_id,
        found_username,
    )
    await last_message.set(sent_message, state)

    await state.set_state(Update.waiting_for_identity)


async def process_identity_handler(
    message: Message,
    state: FSMContext,
    input_id: int,
    input_username: str | None,
    *,
    send_action: SendAction,
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
                send_action,
                user.telegram_id,
                user.username,
                user.role.value,
            )
        except NoResultFound:
            await send_not_found(message, send_action, input_id, input_username)

    await state.set_state(None)


@router.message(Update.waiting_for_identity)
async def user_update_msg_identity_handler(
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
        message, state, input_id, input_username, send_action=SendAction.ANSWER
    )


@router.callback_query(IdentityCallback.filter(F.dir == DIR))
async def user_update_cb_identity_handler(
    callback: CallbackQuery, callback_data: IdentityCallback, state: FSMContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    input_id = callback_data.id
    input_username = callback_data.username

    await process_identity_handler(
        callback.message, state, input_id, input_username, send_action=SendAction.EDIT
    )


async def process_fields_handler(
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
        send_action,
        id,
        edited_id,
        username,
        edited_username,
        role,
        edited_role,
    )

    await state.set_state(None)


@router.callback_query(ConfirmCallback.filter(F.dir == DIR))
async def user_update_confirm_cb_fields_handler(
    callback: CallbackQuery, state: FSMContext
):
    await callback.answer()
    await process_fields_handler(callback.message, state, send_action=SendAction.EDIT)


@router.callback_query(CancelCallback.filter(F.dir == DIR))
async def user_update_cancel_cb_fields_handler(
    callback: CallbackQuery, state: FSMContext
):
    await callback.answer()
    await process_fields_handler(callback.message, state, send_action=SendAction.EDIT)


@router.callback_query(BackCallback.filter(F.dir == DIR))
async def user_update_back_cb_fields_handler(
    callback: CallbackQuery, state: FSMContext
):
    await callback.answer()
    await process_fields_handler(callback.message, state, send_action=SendAction.EDIT)


@router.callback_query(EditCallback.filter(F.dir == DIR and F.field == "username"))
async def user_update_cb_edit_username_handler(
    callback: CallbackQuery, last_message: LastMessage, state: FSMContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    found_username = data.get("found_username", None)

    sent_message = await send_edit_username(
        callback.message, SendAction.EDIT, DIR, found_username
    )
    await last_message.set(sent_message, state)

    await state.set_state(Update.waiting_for_username)


@router.message(Update.waiting_for_username)
async def user_update_msg_edited_username_handler(
    message: Message, last_message: LastMessage, state: FSMContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_username = await process_username_msg(message)
    except ValueError as e:
        sent_message = await send_invalid(message, SendAction.ANSWER, DIR, str(e))
        await last_message.set(sent_message, state)
        return

    await state.update_data(edited_username=input_username)

    await process_fields_handler(message, state, send_action=SendAction.ANSWER)


@router.callback_query(UsernameCallback.filter(F.dir == DIR))
async def user_update_cb_edited_username_handler(
    callback: CallbackQuery, callback_data: UsernameCallback, state: FSMContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    input_username = callback_data.username
    await state.update_data(edited_username=input_username)

    await process_fields_handler(callback.message, state, send_action=SendAction.EDIT)


@router.callback_query(EditCallback.filter(F.dir == DIR and F.field == "role"))
async def user_update_msg_edit_role_handler(
    callback: CallbackQuery, last_message: LastMessage, state: FSMContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    sent_message = await send_edit_role(callback.message, SendAction.EDIT, DIR)
    await last_message.set(sent_message, state)

    await state.set_state(Update.waiting_for_role)


@router.message(Update.waiting_for_role)
async def user_update_msg_edited_role_handler(
    message: Message, last_message: LastMessage, state: FSMContext
):
    await last_message.edit_reply_markup(message, state)

    try:
        input_role = await process_role_msg(message)
    except ValueError as e:
        sent_message = await send_invalid(message, SendAction.ANSWER, DIR, str(e))
        await last_message.set(sent_message, state)
        return

    await state.update_data(edited_role=input_role)

    await process_fields_handler(message, state, send_action=SendAction.ANSWER)


@router.callback_query(RoleCallback.filter(F.dir == DIR))
async def user_update_cb_edited_role_handler(
    callback: CallbackQuery, callback_data: RoleCallback, state: FSMContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    input_role = callback_data.role
    await state.update_data(edited_role=input_role)

    await process_fields_handler(callback.message, state, send_action=SendAction.EDIT)


@router.callback_query(SaveCallback.filter(F.dir == DIR))
async def user_update_cb_save_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    id: int = data.pop("orig_id")
    username: str | None = data.pop("orig_username")
    role: str = data.pop("orig_role")

    edited_username: str | None = data.pop("edited_username", username)
    edited_role: str = data.pop("edited_role", role)

    async with async_session() as session:
        repo = UsersRepository(session)
        service = UsersService(repo)
        try:
            user = await service.update_user(id, edited_username, edited_role)
            await send_successfully_updated(
                callback.message,
                SendAction.EDIT,
                user.telegram_id,
                user.username,
                user.role,
            )
        except NoResultFound:
            await send_not_found(callback.message, SendAction.EDIT, id, username)
        except IntegrityError:
            await send_failed_update(
                callback.message, SendAction.EDIT, "Username already claimed."
            )
