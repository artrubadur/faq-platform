from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger
from sqlalchemy.exc import NoResultFound

from app.core.constants.dirs import USERS_GET
from app.dialogs import SendAction
from app.dialogs.rows.user import IdentityCallback
from app.dialogs.send.admin.user import (
    send_enter_identity,
    send_partially_found,
    send_successfully_found,
)
from app.dialogs.send.common import send_invalid
from app.repositories import UsersRepository
from app.services import UsersService
from app.services.user.process import process_identity_msg
from app.storage.core import async_session
from app.utils.history.last_message import LastMessage

router = Router()

PARENT_DIR, DIR = USERS_GET


class UserFinding(StatesGroup):
    waiting_for_identity = State()


@router.callback_query(F.data == DIR)
async def user_get_cb_handler(
    callback: CallbackQuery, last_message: LastMessage, state: FSMContext
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    sender_id = callback.from_user.id
    sender_username = callback.from_user.username
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
        sender_id,
        sender_username,
    )
    await last_message.set(sent_message, state)

    await state.set_state(UserFinding.waiting_for_identity)


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
            user = await service.get_user(input_id)
            await state.update_data(
                glb_found_user_id=user.telegram_id, glb_found_username=user.username
            )
            logger.debug("User obtained", id=user.id)
            await send_successfully_found(
                message,
                send_action,
                user.telegram_id,
                user.username,
                user.role,
            )
        except NoResultFound:
            await state.update_data(
                glb_found_user_id=input_id, glb_found_username=input_username
            )
            await send_partially_found(message, send_action, input_id, input_username)

    await state.set_state(None)


@router.message(UserFinding.waiting_for_identity)
async def user_get_msg_identity_handler(
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
async def user_get_cb_identity_handler(
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
