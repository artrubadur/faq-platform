import app.dialogs.rows.base as rows
from app.core.constants.emoji import EmojiStatus
from app.dialogs.actions import SendAction, do_action


from aiogram.types import InlineKeyboardMarkup, Message


async def send_invalid(
    message: Message, dir: str, text: str | None, action: SendAction
):
    reply_markup = InlineKeyboardMarkup(inline_keyboard=rows.back_row(dir))
    await do_action(
        message,
        action,
        text=f"{EmojiStatus.WARNING} {text}. Retry or back",
        reply_markup=reply_markup,
    )