from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger
from sqlalchemy.exc import NoResultFound

from app.core.constants.dirs import USERS_DELETE
from app.dialogs import SendAction
from app.dialogs.rows.common import ConfirmCallback
from app.dialogs.rows.user import IdentityCallback
from app.dialogs.send.admin.user import (
    send_confirm_deletion,
    send_enter_identity,
    send_not_found,
    send_successfully_deleted,
)
from app.dialogs.send.common import send_expired, send_invalid
from app.repositories import UsersRepository
from app.services import UsersService
from app.services.user.process import process_identity_msg
from app.storage.core import async_session
from app.utils.history.last_message import LastMessage
from app.utils.state import clear_temp_data, is_expired

router = Router()

PARENT_DIR, DIR = USERS_DELETE


class UserDeletion(StatesGroup):
    waiting_for_identity = State()


@router.callback_query(F.data == DIR)
async def user_delete_cb_handler(
    callback: CallbackQuery, last_message: LastMessage, state: FSMContext
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    found_user_id: int | None = data.get("glb_found_user_id", None)
    found_username: str | None = data.get("glb_found_username", None)

    sent_message = await send_enter_identity(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        PARENT_DIR,
        DIR,
        found_user_id,
        found_username,
    )
    await last_message.set(sent_message, state)

    await state.update_data(tmp_in_operation=True)
    await state.set_state(UserDeletion.waiting_for_identity)


async def process_identity_handler(
    message: Message,
    state: FSMContext,
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
        await send_not_found(message, send_action, input_id, input_username)
        await state.set_state(None)
        return

    await state.update_data(tmp_input_id=input_id)
    await send_confirm_deletion(
        message,
        send_action,
        user.telegram_id,
        user.username,
        user.role,
    )
    await state.set_state(None)


@router.message(UserDeletion.waiting_for_identity)
async def user_delete_msg_identity_handler(
    message: Message, last_message: LastMessage, state: FSMContext
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
async def user_delete_cb_identity_handler(
    callback: CallbackQuery, callback_data: IdentityCallback, state: FSMContext
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


@router.callback_query(ConfirmCallback.filter(F.dir == DIR))
async def user_delete_cb_confirm_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    if is_expired(data):
        await clear_temp_data(state)
        await send_expired(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.ANSWER,
            PARENT_DIR,
        )
        await state.set_state(None)
        return
    
    input_id: int = data.pop("tmp_input_id", None)
    await state.set_data(data)

    try:
        async with async_session() as session:
            repo = UsersRepository(session)
            service = UsersService(repo)
            user = await service.delete_user(input_id)
    except NoResultFound:
        await send_not_found(
            callback.message,  # pyright: ignore[reportArgumentType]
            SendAction.EDIT,
            input_id,
        )
        return

    logger.debug("User deleted", id=user.id)
    await send_successfully_deleted(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        user.telegram_id,
        user.username,
        user.role,
    )
