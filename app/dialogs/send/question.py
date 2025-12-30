from aiogram.types import Message

import app.dialogs.markups.question as mu
from app.core.constants.emoji import EmojiAction, EmojiStatus
from app.dialogs.actions import SendAction, do_action
from app.utils.format.output import format_id, format_question_output


# Input
async def send_enter_question_id(
    message: Message,
    *,
    action: SendAction,
):
    await do_action(
        message,
        action,
        text=f"{EmojiAction.ENTER} Enter the question id",
    )


async def send_enter_question_text(
    message: Message,
    *,
    action: SendAction,
):
    await do_action(
        message,
        action,
        text=f"{EmojiAction.ENTER} Enter the question text",
    )


async def send_enter_answer_text(
    message: Message,
    *,
    action: SendAction,
):
    await do_action(
        message,
        action,
        text=f"{EmojiAction.ENTER} Enter the answer text",
    )


# Creation
async def send_confirm_creation(
    message: Message,
    question_text: str,
    answer_text: str,
    *,
    action: SendAction,
):
    await do_action(
        message,
        action,
        text=(
            f"{EmojiAction.SELECT} Confirm creation?\n"
            f"{format_question_output(
                    question_text=question_text,
                    answer_text=answer_text
                )}"
        ),
        parse_mode="HTML",
        reply_markup=mu.confirm_creation,
    )


async def send_successfully_created(
    message: Message,
    id: int,
    question_text: str,
    answer_text: str,
    *,
    action: SendAction,
):
    await do_action(
        message,
        action,
        text=(
            f"{EmojiStatus.SUCCESSFUL} Question has been successfully created:\n"
            f"{format_question_output(id, question_text, answer_text)}"
        ),
        parse_mode="HTML",
        reply_markup=mu.back,
    )


async def send_found_similar(
    message,
    id,
    question_text,
    *,
    action: SendAction,
):
    await do_action(
        message,
        action,
        text=(
            f"{EmojiStatus.WARNING} A similar question already exists:\n"
            f"{format_question_output(id, question_text)}\n"
            f"{EmojiAction.SELECT} Confirm creation?"
        ),
        parse_mode="HTML",
        reply_markup=mu.confirm_similar,
    )


# async def send_failed_creation( # TODO: USAGE
#     message: Message,
#     exception="Unexcepted error.",
#     *,
#     action: SendAction,
# ):
#     await do_action(
#         message,
#         action,
#         text=format_exception_output(f"Failed to create the question: {exception}"),
#         reply_markup=mu.back,
#     )


# Finding
async def send_successfully_found(
    message: Message,
    id: int,
    question_text: str,
    answer_text: str,
    *,
    action: SendAction,
):
    await do_action(
        message,
        action,
        text=(
            f"{EmojiStatus.SUCCESSFUL} The question has been successfully found:\n"
            f"{format_question_output(id, question_text, answer_text)}"
        ),
        parse_mode="HTML",
        reply_markup=mu.back,
    )


async def send_not_found(message: Message, id: int, *, action: SendAction):
    await do_action(
        message,
        action,
        text=f"{EmojiStatus.FAILED} Question {format_id(id)} not found",
        parse_mode="HTML",
        reply_markup=mu.back,
    )
