from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger

from bot.core.dirs import USERS_GET
from bot.dialogs import SendAction
from bot.dialogs.rows.user import IdentityCallback
from bot.dialogs.send.admin.user import (
    send_enter_identity,
    send_partially_found,
    send_successfully_found,
)
from bot.dialogs.send.common import send_invalid
from bot.services.api.exceptions import NotFoundError
from bot.services.user.gateway import user_gateway
from bot.services.user.process import process_identity_msg
from bot.utils.state.history import LastMessage
from bot.utils.state.temp import TempContext

router = Router()

PARENT_DIR, DIR = USERS_GET


class UserFinding(StatesGroup):
    waiting_for_identity = State()


@router.callback_query(F.data == DIR)
async def user_get_cb_handler(
    callback: CallbackQuery, last_message: LastMessage, state: TempContext
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    sender_id = callback.from_user.id
    sender_username = callback.from_user.username
    data = await state.storage.get_data(
        state.key,
    )
    found_user_id: int | None = data.get("found_user_id", None)
    found_username: str | None = data.get("found_username", None)

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
        await state.storage.update_data(
            state.key,
            {"found_user_id": input_id, "found_username": input_username},
            "long",
        )
        logger.debug("User partially obtained", id=input_id)
        return

    await send_partially_found(message, send_action, input_id, input_username)

    await state.storage.update_data(
        state.key,
        {"found_user_id": user.telegram_id, "found_username": user.username},
        "long",
    )

    await state.clear()

    logger.debug("User obtained", id=user.id)
    await send_successfully_found(
        message,
        send_action,
        user.telegram_id,
        user.username,
        user.role,
    )


@router.message(UserFinding.waiting_for_identity)
async def user_get_msg_identity_handler(
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
async def user_get_cb_identity_handler(
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
