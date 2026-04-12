from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger

from bot.core.dirs import FORMULATIONS_LIST
from bot.dialogs.actions import SendAction
from bot.dialogs.rows.common import (
    CancelCallback,
    PaginOrderCallback,
    PaginPageCallback,
    PaginSizeCallback,
)
from bot.dialogs.rows.formulation import ScopeCallback
from bot.dialogs.send.admin.formulation import (
    send_empty_pagination,
    send_enter_filter_question_id,
    send_pagination,
)
from bot.dialogs.send.common import send_expired, send_invalid
from bot.services.common.process import process_page_msg
from bot.services.common.validate import resolve_page
from bot.services.formulation.gateway import formulation_gateway
from bot.services.formulation.process import process_question_id_msg
from bot.utils.state.history import LastMessage
from bot.utils.state.operation import is_operation_expired, start_operation
from bot.utils.state.temp import TempContext
from shared.api.exceptions import NotFoundError
from shared.contracts.formulation.requests import FormulationFields

router = Router()

PARENT_DIR, DIR = FORMULATIONS_LIST


class FormulationListing(StatesGroup):
    waiting_for_page = State()
    waiting_for_filter_question_id = State()


async def process(
    message: Message,
    last_message: LastMessage,
    state: TempContext,
    *,
    send_action: SendAction,
):
    data = await state.get_data()
    if is_operation_expired(data):
        await state.clear()
        return await send_expired(
            message,
            SendAction.ANSWER,
            PARENT_DIR,
        )

    order: FormulationFields = data["order"]
    ascending: bool = data["ascending"]
    page: int = data["page"]
    page_size: int = data["page_size"]
    question_id_scope: int | None = data.get("question_id_scope")

    try:
        amount = await formulation_gateway.get_formulations_amount(question_id_scope)
    except NotFoundError as exc:
        await send_invalid(message, send_action, PARENT_DIR, str(exc))
        return

    max_page = (amount + page_size - 1) // page_size
    page = resolve_page(page, max_page)
    await state.update_data(page=page)

    if page == 0:
        logger.debug("No formulations found")
        await send_empty_pagination(message, send_action, question_id_scope)
        return

    try:
        formulations = await formulation_gateway.get_paginated_formulations(
            page,
            page_size,
            order,
            ascending,
            question_id_scope,
        )
    except NotFoundError as exc:
        await send_invalid(message, send_action, PARENT_DIR, str(exc))
        return

    logger.debug("Formulations obtained", len=len(formulations))
    sent_message = await send_pagination(
        message,
        send_action,
        formulations,
        order,
        ascending,
        page,
        max_page,
        page_size,
        question_id_scope,
    )
    await last_message.set(sent_message, state)


@router.callback_query(F.data == DIR)
async def formulation_list_cb_handler(
    callback: CallbackQuery,
    last_message: LastMessage,
    state: TempContext,
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    await start_operation(
        state,
        order="id",
        ascending=True,
        page=1,
        page_size=5,
        question_id_scope=None,
    )

    await process(
        callback.message,  # pyright: ignore[reportArgumentType],
        last_message,
        state,
        send_action=SendAction.EDIT,
    )

    await state.set_state(FormulationListing.waiting_for_page)


@router.message(FormulationListing.waiting_for_page)
async def formulation_list_msg_page_handler(
    message: Message,
    last_message: LastMessage,
    state: TempContext,
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
async def formulation_list_cb_page_handler(
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
async def formulation_list_cb_size_handler(
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
async def formulation_list_cb_order_handler(
    callback: CallbackQuery,
    last_message: LastMessage,
    callback_data: PaginOrderCallback,
    state: TempContext,
):
    await callback.answer()

    new_order = callback_data.column
    data = await state.get_data()
    if data.get("order", "") == new_order:
        await state.update_data(ascending=(not data.get("ascending", False)))
    else:
        await state.update_data(order=new_order)

    await process(
        callback.message,  # pyright: ignore[reportArgumentType]
        last_message,
        state,
        send_action=SendAction.EDIT,
    )


@router.callback_query(ScopeCallback.filter((F.dir == DIR) & ~F.cancel))
async def formulation_list_cb_scope_filter_handler(
    callback: CallbackQuery,
    last_message: LastMessage,
    state: TempContext,
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    sent_message = await send_enter_filter_question_id(
        callback.message,  # pyright: ignore[reportArgumentType]
        SendAction.EDIT,
        DIR,
    )
    await last_message.set(sent_message, state)

    await state.set_state(FormulationListing.waiting_for_filter_question_id)


@router.callback_query(ScopeCallback.filter((F.dir == DIR) & F.cancel))
async def formulation_list_cb_scope_cancel_handler(
    callback: CallbackQuery,
    last_message: LastMessage,
    state: TempContext,
):
    await callback.answer()

    await state.update_data(question_id_scope=None, page=1)

    await process(
        callback.message,  # pyright: ignore[reportArgumentType]
        last_message,
        state,
        send_action=SendAction.EDIT,
    )

    await state.set_state(FormulationListing.waiting_for_page)


@router.message(FormulationListing.waiting_for_filter_question_id)
async def formulation_list_msg_filter_question_id_handler(
    message: Message,
    last_message: LastMessage,
    state: TempContext,
):
    await last_message.delete(message, state)

    try:
        input_question_id = process_question_id_msg(message)
    except ValueError as exc:
        sent_message = await send_invalid(
            message, SendAction.ANSWER, PARENT_DIR, str(exc)
        )
        await last_message.set(sent_message, state)
        return

    await state.update_data(question_id_scope=input_question_id, page=1)

    await process(
        message,
        last_message,
        state,
        send_action=SendAction.ANSWER,
    )

    await state.set_state(FormulationListing.waiting_for_page)


@router.callback_query(CancelCallback.filter(F.dir == DIR))
async def formulation_list_cb_cancel_filter_input_handler(
    callback: CallbackQuery,
    last_message: LastMessage,
    state: TempContext,
):
    await callback.answer()

    await process(
        callback.message,  # pyright: ignore[reportArgumentType]
        last_message,
        state,
        send_action=SendAction.EDIT,
    )

    await state.set_state(FormulationListing.waiting_for_page)
