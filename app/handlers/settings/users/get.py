# pyright: reportArgumentType=false
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.exc import NoResultFound

from app.dialogs import SendAction
from app.dialogs.rows.user import IdentityCallback
from app.dialogs.send.user import (
    send_enter_identity,
    send_invalid,
    send_partially_found,
    send_successfully_found,
)
from app.repositories import UsersRepository
from app.services import UsersService
from app.services.user.process import process_identity_msg
from app.storage.db.engine import async_session

router = Router()

PARENT_DIR = "settings.users"
DIR = "settings.users.get"


class Finding(StatesGroup):
    waiting_for_id = State()


# Entry point
@router.callback_query(F.data == DIR)
async def cb_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    sender_id = callback.from_user.id
    sender_username = callback.from_user.username
    data = await state.get_data()
    found_id: int | None = data.get("found_id", None)
    found_username = data.get("found_username", None)

    await send_enter_identity(
        callback.message,
        DIR,
        found_id,
        found_username,
        sender_id,
        sender_username,
        action=SendAction.EDIT,
    )
    await state.set_state(Finding.waiting_for_id)


# Result
async def process_result_handler(
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
                found_id=user.telegram_id, found_username=user.username
            )
            await send_successfully_found(
                message,
                user.telegram_id,
                user.username,
                user.role,
                action=send_action,
            )
        except NoResultFound:
            await state.update_data(found_id=input_id, found_username=input_username)
            await send_partially_found(
                message, input_id, input_username, action=send_action
            )

    await state.set_state(None)


@router.message(Finding.waiting_for_id)
async def msg_result_handler(message: Message, state: FSMContext):
    try:
        input_id, input_username = await process_identity_msg(message)
    except ValueError as e:
        await send_invalid(message, PARENT_DIR, str(e), action=SendAction.ANSWER)
        return

    await process_result_handler(
        message, state, input_id, input_username, send_action=SendAction.ANSWER
    )


@router.callback_query(IdentityCallback.filter(F.dir == DIR))
async def cb_result_handler(
    callback: CallbackQuery, callback_data: IdentityCallback, state: FSMContext
):
    await callback.answer("")
    await callback.message.edit_reply_markup(reply_markup=None)

    input_id = callback_data.id
    input_username = callback_data.username

    await process_result_handler(
        callback.message, state, input_id, input_username, send_action="edit"
    )
