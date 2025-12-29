from aiogram.types import InlineKeyboardMarkup, Message, ReplyKeyboardRemove

import app.dialogs.rows.root as rows
from app.core.constants.emoji import EmojiAction
from app.core.constants.files import Images
from app.dialogs.actions import SendAction, do_action
from app.utils.format.output import format_exception_output


async def send_start(message: Message, *, action: SendAction):
    await do_action(
        message,
        action,
        document=Images.GREETING.value,
        caption=f"You started the bot, {message.from_user.full_name}!",
        reply_markup=ReplyKeyboardRemove(),
    )


async def send_confirm_goto(message: Message, dir: str, *, action: SendAction):
    reply_markup = InlineKeyboardMarkup(inline_keyboard=rows.go_row(dir))

    await do_action(
        message,
        action,
        text=f"{EmojiAction.SELECT} Go to `{dir}`?",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


async def send_invalid_path(
    message: Message, exception: str | None = None, *, action: SendAction
):
    await do_action(
        message,
        action,
        text=format_exception_output(f"Failed to go: {exception}"),
    )
