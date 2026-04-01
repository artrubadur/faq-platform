from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger

from bot.core.dirs import USERS_LIST
from bot.dialogs.actions import SendAction
from bot.dialogs.rows.common import (
    PaginOrderCallback,
    PaginPageCallback,
    PaginSizeCallback,
)
from bot.dialogs.send.admin.user import send_empty_pagination, send_pagination
from bot.dialogs.send.common import send_expired, send_invalid
from bot.services.common.process import process_page_msg
from bot.services.user.gateway import user_gateway
from bot.utils.state.history import LastMessage, is_expired
from bot.utils.state.temp import TempContext

router = Router()

PARENT_DIR, DIR = USERS_LIST


class UserListing(StatesGroup):
    waiting_for_page = State()


async def process(
    message: Message,
    last_message: LastMessage,
    state: TempContext,
    *,
    send_action: SendAction
):
    data = await state.get_data()
    if is_expired(data):
        await state.clear()
        await send_expired(
            message,
            SendAction.ANSWER,
            PARENT_DIR,
        )
        return
    await state.set_data(data)

    order: str = data["order"]
    ascending: bool = data["ascending"]
    page: int = data["page"]
    page_size: int = data["page_size"]

    if "amount" not in data:
        amount = await user_gateway.get_user_amount()
        await state.update_data(amount=amount)
    else:
        amount = data["amount"]

    max_page = (amount + page_size - 1) // page_size
    page = min(max_page, page)
    if page == 0:
        logger.debug("No users found")
        return await send_empty_pagination(message, send_action)
    users = await user_gateway.get_paginated_users(page, page_size, order, ascending)

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
    callback: CallbackQuery, last_message: LastMessage, state: TempContext
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    await state.set_data(
        {
            "order": "id",
            "ascending": True,
            "page": 1,
            "page_size": 5,
            "in_operation": True,
        }
    )

    await process(
        callback.message,  # pyright: ignore[reportArgumentType]
        last_message,
        state,
        send_action=SendAction.EDIT,
    )

    await state.update_data(in_operation=True)
    await state.set_state(UserListing.waiting_for_page)


@router.message(UserListing.waiting_for_page)
async def user_list_msg_page_handler(
    message: Message, last_message: LastMessage, state: TempContext
):
    await last_message.delete(message, state)

    try:
        input_page = process_page_msg(message)
    except ValueError as exc:
        sent_message = await send_invalid(
            message, SendAction.ANSWER, PARENT_DIR, str(exc)
        )
        await last_message.set(sent_message, state)
        return

    await state.update_data(page=input_page)

    await process(message, last_message, state, send_action=SendAction.ANSWER)


@router.callback_query(PaginPageCallback.filter(F.dir == DIR))
async def user_list_cb_page_handler(
    callback: CallbackQuery,
    last_message: LastMessage,
    callback_data: PaginPageCallback,
    state: TempContext,
):
    await callback.answer()

    data = await state.get_data()
    page = max(1, data.get("page", 1) + callback_data.page)
    await state.update_data(page=page)

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
    state: TempContext,
):
    await callback.answer()

    await state.update_data(page_size=callback_data.size)

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
    state: TempContext,
):
    await callback.answer()

    new_order = callback_data.column
    data = await state.get_data()
    if data["order"] == new_order:
        await state.update_data(ascending=(not data["ascending"]))
    else:
        await state.update_data(order=new_order)

    await process(
        callback.message,  # pyright: ignore[reportArgumentType]
        last_message,
        state,
        send_action=SendAction.EDIT,
    )
