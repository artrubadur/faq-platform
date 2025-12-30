# pyright: reportArgumentType=false
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.exc import NoResultFound

from app.dialogs import SendAction
from app.dialogs.rows.base import ConfirmCallback
from app.dialogs.rows.user import IdentityCallback
from app.dialogs.send.base import send_invalid
from app.dialogs.send.user import (
    send_confirm_deletion,
    send_enter_identity,
    send_not_found,
    send_successfully_deleted,
)
from app.repositories import UsersRepository
from app.services import UsersService
from app.services.user.process import process_identity_msg
from app.storage.db.engine import async_session

router = Router()

PARENT_DIR = "settings.users"
DIR = "settings.users.delete"


class Deletion(StatesGroup):
    waiting_for_identity = State()


@router.callback_query(F.data == DIR)
async def user_delete_cb_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

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
    await state.set_state(Deletion.waiting_for_identity)


async def process_identity_handler(
    message: Message,
    state: FSMContext,
    input_id: int,
    input_username: str | None,
    *,
    send_action: SendAction
):
    await state.update_data(input_id=input_id)

    async with async_session() as session:
        repo = UsersRepository(session)
        service = UsersService(repo)
        try:
            user = await service.read_user(input_id)
            await send_confirm_deletion(
                message,
                user.telegram_id,
                user.username,
                user.role.value,
                action=send_action,
            )
        except NoResultFound:
            await send_not_found(message, input_id, input_username, action=send_action)

    await state.set_state(None)


@router.message(Deletion.waiting_for_identity)
async def user_delete_msg_identity_handler(message: Message, state: FSMContext):
    try:
        input_id, input_username = await process_identity_msg(message)
    except ValueError as e:
        await send_invalid(message, PARENT_DIR, str(e), action=SendAction.ANSWER)
        return

    await process_identity_handler(
        message, state, input_id, input_username, send_action=SendAction.ANSWER
    )


@router.callback_query(IdentityCallback.filter(F.dir == DIR))
async def user_delete_cb_identity_handler(
    callback: CallbackQuery, callback_data: IdentityCallback, state: FSMContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    input_id = callback_data.id
    input_username = callback_data.username

    await process_identity_handler(
        callback.message, state, input_id, input_username, send_action=SendAction.EDIT
    )


@router.callback_query(ConfirmCallback.filter(F.dir == DIR))
async def user_delete_cb_confirm_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    input_id: int = data.pop("input_id")

    async with async_session() as session:
        repo = UsersRepository(session)
        service = UsersService(repo)
        try:
            user = await service.delete_user(input_id)
            await send_successfully_deleted(
                callback.message,
                user.telegram_id,
                user.username,
                user.role,
                action=SendAction.EDIT,
            )
        except NoResultFound:
            await send_not_found(callback.message, input_id, action=SendAction.EDIT)

    await state.set_state(None)
