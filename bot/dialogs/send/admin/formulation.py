from typing import Awaitable, Callable

from aiogram.types import InlineKeyboardMarkup, Message

import bot.dialogs.markups.formulation as mu
import bot.dialogs.rows.common as brows
import bot.dialogs.rows.formulation as frows
from bot.core.customization import messages
from bot.dialogs.actions import with_message_action
from bot.utils.format.output import (
    format_edited_formulation,
    format_exception,
    format_formulation,
    format_formulation_table,
    format_id,
)
from shared.contracts.formulation.responses import FormulationResponse


# Input
@with_message_action
async def send_enter_id(
    send: Callable[..., Awaitable[Message]],
    cancel_dir: str,
    dir: str,
    found_formulation_id: int | None = None,
) -> Message:
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=frows.id_row(dir, found_formulation_id)
        + brows.cancel_row(cancel_dir)
    )
    return await send(
        text=messages.responses.admin.formulation.enter.id,
        parse_mode=messages.parse_mode,
        reply_markup=reply_markup,
    )


@with_message_action
async def send_enter_question_text(
    send: Callable[..., Awaitable[Message]],
    cancel_dir: str,
) -> Message:
    reply_markup = InlineKeyboardMarkup(inline_keyboard=brows.cancel_row(cancel_dir))
    return await send(
        text=messages.responses.admin.formulation.enter.question_text,
        parse_mode=messages.parse_mode,
        reply_markup=reply_markup,
    )


@with_message_action
async def send_enter_question_id(
    send: Callable[..., Awaitable[Message]],
    cancel_dir: str,
) -> Message:
    reply_markup = InlineKeyboardMarkup(inline_keyboard=brows.cancel_row(cancel_dir))
    return await send(
        text=messages.responses.admin.formulation.enter.question_id,
        parse_mode=messages.parse_mode,
        reply_markup=reply_markup,
    )


@with_message_action
async def send_enter_filter_question_id(
    send: Callable[..., Awaitable[Message]],
    cancel_dir: str,
) -> Message:
    reply_markup = InlineKeyboardMarkup(inline_keyboard=brows.cancel_row(cancel_dir))
    return await send(
        text=messages.responses.admin.formulation.enter.filter_question_id,
        parse_mode=messages.parse_mode,
        reply_markup=reply_markup,
    )


# Creation
@with_message_action
async def send_confirm_creation(
    send: Callable[..., Awaitable[Message]],
    question_id: int,
    question_text: str,
) -> Message:
    return await send(
        text=messages.responses.admin.formulation.creation.confirm.format(
            formulation=format_formulation(
                question_id=question_id,
                question_text=question_text,
            )
        ),
        parse_mode=messages.parse_mode,
        reply_markup=mu.confirm_creation,
    )


@with_message_action
async def send_successfully_created(
    send: Callable[..., Awaitable[Message]],
    id: int,
    question_id: int,
    question_text: str,
) -> Message:
    return await send(
        text=messages.responses.admin.formulation.creation.successful.format(
            formulation=format_formulation(
                id=id,
                question_id=question_id,
                question_text=question_text,
            )
        ),
        parse_mode=messages.parse_mode,
        reply_markup=mu.back,
    )


@with_message_action
async def send_embedding_failed(
    send: Callable[..., Awaitable[Message]],
    cancel_dir: str,
) -> Message:
    reply_markup = InlineKeyboardMarkup(inline_keyboard=brows.cancel_row(cancel_dir))

    return await send(
        text=messages.exceptions.formulation.embedding_failed,
        parse_mode=messages.parse_mode,
        reply_markup=reply_markup,
    )


# Finding
@with_message_action
async def send_successfully_found(
    send: Callable[..., Awaitable[Message]],
    id: int,
    question_id: int,
    question_text: str,
) -> Message:
    return await send(
        text=messages.responses.admin.formulation.finding.successful.format(
            formulation=format_formulation(
                id=id,
                question_id=question_id,
                question_text=question_text,
            )
        ),
        parse_mode=messages.parse_mode,
        reply_markup=mu.back,
    )


@with_message_action
async def send_not_found(send: Callable[..., Awaitable[Message]], id: int) -> Message:
    return await send(
        text=format_exception(
            messages.exceptions.formulation.not_found.format(id=format_id(id))
        ),
        parse_mode=messages.parse_mode,
        reply_markup=mu.back,
    )


# Deletion
@with_message_action
async def send_confirm_deletion(
    send: Callable[..., Awaitable[Message]],
    id: int,
    question_id: int,
    question_text: str,
) -> Message:
    return await send(
        text=messages.responses.admin.formulation.deletion.confirm.format(
            formulation=format_formulation(
                id=id,
                question_id=question_id,
                question_text=question_text,
            )
        ),
        parse_mode=messages.parse_mode,
        reply_markup=mu.confirm_deletion,
    )


@with_message_action
async def send_successfully_deleted(
    send: Callable[..., Awaitable[Message]],
    id: int,
    question_id: int,
    question_text: str,
) -> Message:
    return await send(
        text=messages.responses.admin.formulation.deletion.successful.format(
            formulation=format_formulation(
                id=id,
                question_id=question_id,
                question_text=question_text,
            )
        ),
        parse_mode=messages.parse_mode,
        reply_markup=mu.back,
    )


# Update
@with_message_action
async def send_confirm_update(
    send: Callable[..., Awaitable[Message]],
    id: int,
    question_id: int,
    question_text: str,
) -> Message:
    return await send(
        text=messages.responses.admin.formulation.update.confirm.format(
            formulation=format_formulation(
                id=id,
                question_id=question_id,
                question_text=question_text,
            )
        ),
        parse_mode=messages.parse_mode,
        reply_markup=mu.confirm_update,
    )


@with_message_action
async def send_changes(
    send: Callable[..., Awaitable[Message]],
    id: int,
    question_id: int,
    edited_question_id: int,
    question_text: str,
    edited_question_text: str,
    recompute_embedding: bool,
) -> Message:
    changes_text = format_edited_formulation(
        id,
        question_id,
        edited_question_id,
        question_text,
        edited_question_text,
        recompute_embedding,
    )
    return await send(
        text=messages.responses.admin.formulation.update.select_field.format(
            formulation=changes_text
        ),
        parse_mode=messages.parse_mode,
        reply_markup=mu.field_save_update,
    )


@with_message_action
async def send_confirm_recompute(
    send: Callable[..., Awaitable[Message]],
) -> Message:
    return await send(
        text=messages.responses.admin.formulation.update.confirm_recompute,
        parse_mode=messages.parse_mode,
        reply_markup=mu.confirm_recompute,
    )


@with_message_action
async def send_successfully_updated(
    send: Callable[..., Awaitable[Message]],
    id: int,
    question_id: int,
    question_text: str,
) -> Message:
    return await send(
        text=messages.responses.admin.formulation.update.successful.format(
            formulation=format_formulation(
                id=id,
                question_id=question_id,
                question_text=question_text,
            )
        ),
        parse_mode=messages.parse_mode,
        reply_markup=mu.back,
    )


@with_message_action
async def send_pagination(
    send: Callable[..., Awaitable[Message]],
    formulations: list[FormulationResponse],
    order: str,
    ascending: bool,
    page: int,
    max_page: int,
    page_size: int,
    question_id_scope: int | None,
) -> Message:

    has_prev = page > 1
    has_next = page != max_page
    index_offset = (page - 1) * page_size

    columns = list(FormulationResponse.model_fields)

    reply_markup = mu.make_listing_markup(
        columns,
        order,
        ascending,
        page_size,
        has_prev,
        has_next,
        question_id_scope,
    )

    table = format_formulation_table(formulations, columns, index_offset)
    text = messages.responses.admin.formulation.listing.successful.format(
        page=page,
        max_page=max_page,
        content=table,
        scope=(
            messages.responses.admin.formulation.listing.scope.format(
                question_id=question_id_scope
            )
            if question_id_scope is not None
            else ""
        ),
    )
    return await send(
        text=text,
        reply_markup=reply_markup,
        parse_mode=messages.parse_mode,
    )


@with_message_action
async def send_empty_pagination(
    send: Callable[..., Awaitable[Message]],
    question_id_scope: int | None,
) -> Message:
    text = (
        messages.responses.admin.formulation.listing.not_found_scoped.format(
            question_id=question_id_scope
        )
        if question_id_scope is not None
        else messages.responses.admin.formulation.listing.not_found
    )
    return await send(
        text=text,
        parse_mode=messages.parse_mode,
        reply_markup=mu.back,
    )
