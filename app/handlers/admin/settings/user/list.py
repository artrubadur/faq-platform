from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger

from app.core.constants.dirs import USERS_LIST
from app.dialogs.actions import SendAction
from app.dialogs.rows.common import (
    PaginOrderCallback,
    PaginPageCallback,
    PaginSizeCallback,
)
from app.dialogs.send.admin.user import send_empty_pagination, send_pagination
from app.dialogs.send.common import send_invalid
from app.repositories import UsersRepository
from app.services import UsersService
from app.services.common.process import process_page_msg
from app.storage.core import async_session
from app.utils.history.last_message import LastMessage

router = Router()

PARENT_DIR, DIR = USERS_LIST


class UserListing(StatesGroup):
    waiting_for_page = State()


async def process(
    message: Message,
    last_message: LastMessage,
    state: FSMContext,
    *,
    send_action: SendAction
):
    data = await state.get_data()
    order: str = data["tmp_order"]
    ascending: bool = data["tmp_ascending"]
    page: int = data["tmp_page"]
    page_size: int = data["tmp_page_size"]

    async with async_session() as session:
        repo = UsersRepository(session)
        service = UsersService(repo)

        if "tmp_amount" not in data:
            amount = await service.get_user_amount()
            await state.update_data(tmp_amount=amount)
        else:
            amount = data["tmp_amount"]

        max_page = (amount + page_size - 1) // page_size
        page = min(max_page, page)
        if page == 0:
            logger.debug("No users found")
            await send_empty_pagination(message, send_action)
            return

        users = await service.get_paginated_users(page, page_size, order, ascending)
        logger.debug("Users obtained", len=len(users))
        sent_message = await send_pagination(
            message,
            send_action,
            users,
            order,
            ascending,
            page,
            max_page,
            page_size,
        )
        await last_message.set(sent_message, state)


@router.callback_query(F.data == DIR)
async def user_list_cb_handler(
    callback: CallbackQuery, last_message: LastMessage, state: FSMContext
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    await state.update_data(
        tmp_order="id", tmp_ascending=True, tmp_page=1, tmp_page_size=5
    )

    await process(
        callback.message,  # pyright: ignore[reportArgumentType]
        last_message,
        state,
        send_action=SendAction.EDIT,
    )

    await state.set_state(UserListing.waiting_for_page)


@router.message(UserListing.waiting_for_page)
async def user_list_msg_page_handler(
    message: Message, last_message: LastMessage, state: FSMContext
):
    await last_message.delete(message, state)

    try:
        input_page = await process_page_msg(message)
    except ValueError as e:
        sent_message = await send_invalid(
            message, SendAction.ANSWER, PARENT_DIR, str(e)
        )
        await last_message.set(sent_message, state)
        return

    await state.update_data(tmp_page=input_page)

    await process(message, last_message, state, send_action=SendAction.ANSWER)


@router.callback_query(PaginPageCallback.filter(F.dir == DIR))
async def user_list_cb_page_handler(
    callback: CallbackQuery,
    last_message: LastMessage,
    callback_data: PaginPageCallback,
    state: FSMContext,
):
    await callback.answer()

    data = await state.get_data()
    page = max(1, data.get("tmp_page", 1) + callback_data.page)
    await state.update_data(tmp_page=page)

    await process(
        callback.message,  # pyright: ignore[reportArgumentType]
        last_message,
        state,
        send_action=SendAction.EDIT,
    )


@router.callback_query(PaginSizeCallback.filter(F.dir == DIR))
async def user_list_cb_size_handler(
    callback: CallbackQuery,
    last_message: LastMessage,
    callback_data: PaginSizeCallback,
    state: FSMContext,
):
    await callback.answer()

    await state.update_data(tmp_page_size=callback_data.size)

    await process(
        callback.message,  # pyright: ignore[reportArgumentType]
        last_message,
        state,
        send_action=SendAction.EDIT,
    )


@router.callback_query(PaginOrderCallback.filter(F.dir == DIR))
async def user_list_cb_order_handler(
    callback: CallbackQuery,
    last_message: LastMessage,
    callback_data: PaginOrderCallback,
    state: FSMContext,
):
    await callback.answer()

    new_order = callback_data.column
    data = await state.get_data()
    if data["tmp_order"] == new_order:
        await state.update_data(tmp_ascending=(not data["tmp_ascending"]))
    else:
        await state.update_data(tmp_order=new_order)

    await process(
        callback.message,  # pyright: ignore[reportArgumentType]
        last_message,
        state,
        send_action=SendAction.EDIT,
    )
