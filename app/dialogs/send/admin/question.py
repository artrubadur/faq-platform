from typing import Awaitable, Callable

from aiogram.types import InlineKeyboardMarkup, Message

import app.dialogs.markups.question as mu
import app.dialogs.rows.common as brows
import app.dialogs.rows.question as qrows
from app.core.customization import messages
from app.dialogs.actions import with_message_action
from app.repositories.questions import QuestionColumn
from app.storage.models.question import Question
from app.utils.format.output import (
    format_edited_question,
    format_exception,
    format_id,
    format_question,
    format_question_table,
)


# Input
@with_message_action
async def send_enter_id(
    send: Callable[..., Awaitable[Message]],
    cancel_dir: str,
    dir: str,
    found_question_id: int | None = None,
) -> Message:
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=qrows.id_row(dir, found_question_id)
        + brows.cancel_row(cancel_dir)
    )
    return await send(
        text=messages.responses.admin.question.enter.id,
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
        text=messages.responses.admin.question.enter.question_text,
        parse_mode=messages.parse_mode,
        reply_markup=reply_markup,
    )


@with_message_action
async def send_enter_answer_text(
    send: Callable[..., Awaitable[Message]],
    cancel_dir: str,
) -> Message:
    reply_markup = InlineKeyboardMarkup(inline_keyboard=brows.cancel_row(cancel_dir))
    return await send(
        text=messages.responses.admin.question.enter.answer_text,
        parse_mode=messages.parse_mode,
        reply_markup=reply_markup,
    )


@with_message_action
async def send_enter_rating(
    send: Callable[..., Awaitable[Message]], dir: str
) -> Message:
    reply_markup = InlineKeyboardMarkup(inline_keyboard=brows.cancel_row(dir))

    return await send(
        text=messages.responses.admin.question.enter.rating,
        parse_mode=messages.parse_mode,
        reply_markup=reply_markup,
    )


# Creation
@with_message_action
async def send_confirm_creation(
    send: Callable[..., Awaitable[Message]],
    question_text: str,
    answer_text: str,
) -> Message:
    return await send(
        text=messages.responses.admin.question.creation.confirm.format(
            question=format_question(
                question_text=question_text, answer_text=answer_text
            )
        ),
        parse_mode=messages.parse_mode,
        reply_markup=mu.confirm_creation,
    )


@with_message_action
async def send_successfully_created(
    send: Callable[..., Awaitable[Message]],
    id: int,
    question_text: str,
    answer_text: str,
) -> Message:
    return await send(
        text=messages.responses.admin.question.creation.successful.format(
            question=format_question(id, question_text, answer_text)
        ),
        parse_mode=messages.parse_mode,
        reply_markup=mu.back,
    )


@with_message_action
async def send_found_similar(
    send: Callable[..., Awaitable[Message]],
    id: int,
    question_text: str,
) -> Message:
    return await send(
        text=format_exception(
            messages.exceptions.question.similar,
            question=format_question(id, question_text),
        ),
        parse_mode=messages.parse_mode,
        reply_markup=mu.confirm_similar,
    )


# Finding
@with_message_action
async def send_successfully_found(
    send: Callable[..., Awaitable[Message]],
    id: int,
    question_text: str,
    answer_text: str,
) -> Message:
    return await send(
        text=messages.responses.admin.question.finding.successful.format(
            question=format_question(id, question_text, answer_text)
        ),
        parse_mode=messages.parse_mode,
        reply_markup=mu.back,
    )


@with_message_action
async def send_not_found(send: Callable[..., Awaitable[Message]], id: int) -> Message:
    return await send(
        text=format_exception(
            messages.exceptions.question.not_found.format(id=format_id(id))
        ),
        parse_mode=messages.parse_mode,
        reply_markup=mu.back,
    )


# Delition
@with_message_action
async def send_confirm_deletion(
    send: Callable[..., Awaitable[Message]],
    id: int,
    question_text: str,
    answer_text: str,
) -> Message:
    return await send(
        text=messages.responses.admin.question.deletion.confirm.format(
            question=format_question(id, question_text, answer_text)
        ),
        parse_mode=messages.parse_mode,
        reply_markup=mu.confirm_deletion,
    )


@with_message_action
async def send_successfully_deleted(
    send: Callable[..., Awaitable[Message]],
    id: int,
    question_text: str,
    answer_text: str,
) -> Message:
    return await send(
        text=messages.responses.admin.question.deletion.successful.format(
            question=format_question(id, question_text, answer_text)
        ),
        parse_mode=messages.parse_mode,
        reply_markup=mu.back,
    )


# Update
@with_message_action
async def send_confirm_update(
    send: Callable[..., Awaitable[Message]],
    id: int,
    question_text: str,
    answer_text: str,
) -> Message:
    return await send(
        text=messages.responses.admin.question.update.confirm.format(
            question=format_question(id, question_text, answer_text)
        ),
        parse_mode=messages.parse_mode,
        reply_markup=mu.confirm_update,
    )


@with_message_action
async def send_changes(
    send: Callable[..., Awaitable[Message]],
    id: int,
    question_text: str,
    edited_question_text: str,
    answer_text: str,
    edited_answer_text: str,
    rating: float,
    edited_rating: float,
    recompute_embedding: bool,
) -> Message:
    changes_text = format_edited_question(
        id,
        question_text,
        edited_question_text,
        answer_text,
        edited_answer_text,
        rating,
        edited_rating,
        recompute_embedding,
    )
    return await send(
        text=messages.responses.admin.question.update.select_field.format(
            question=changes_text
        ),
        parse_mode=messages.parse_mode,
        reply_markup=mu.field_save_update,
    )


@with_message_action
async def send_confirm_recompute(
    send: Callable[..., Awaitable[Message]],
) -> Message:
    return await send(
        text=messages.responses.admin.question.update.confirm_recompute,
        parse_mode=messages.parse_mode,
        reply_markup=mu.confirm_recompute,
    )


@with_message_action
async def send_successfully_updated(
    send: Callable[..., Awaitable[Message]],
    id: int,
    question_text: str,
    answer_text: str,
    rating: float,
) -> Message:
    return await send(
        text=messages.responses.admin.question.update.successful.format(
            question=format_question(id, question_text, answer_text, rating)
        ),
        parse_mode=messages.parse_mode,
        reply_markup=mu.back,
    )


@with_message_action
async def send_pagination(
    send: Callable[..., Awaitable[Message]],
    questions: list[Question],
    order: str,
    ascending: bool,
    page: int,
    max_page: int,
    page_size: int,
) -> Message:

    has_prev = page > 1
    has_next = page != max_page
    index_offset = (page - 1) * page_size

    columns = [m.value for m in QuestionColumn][:-1]

    reply_markup = mu.make_listing_markup(
        columns, order, ascending, page_size, has_prev, has_next
    )

    table = format_question_table(questions, columns, index_offset)
    text = messages.responses.admin.question.listing.successful.format(
        page=page, max_page=max_page, content=table
    )
    return await send(text=text, reply_markup=reply_markup, parse_mode="Markdown")


@with_message_action
async def send_empty_pagination(
    send: Callable[..., Awaitable[Message]],
) -> Message:
    return await send(
        text=messages.responses.admin.question.listing.not_found,
        parse_mode=messages.parse_mode,
        reply_markup=mu.back,
    )
