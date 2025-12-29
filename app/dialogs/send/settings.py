from aiogram.types import InlineKeyboardMarkup, Message

import app.dialogs.rows.base as brows
import app.dialogs.rows.settings as srows
from app.core.constants.emoji import EmojiMenu
from app.dialogs.actions import SendAction, do_action


async def send_menu(message: Message, *, action: SendAction):
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=srows.section_rows() + brows.close_row()
    )

    await do_action(
        message,
        action,
        text=f"{EmojiMenu.SETTINGS} Settings",
        reply_markup=reply_markup,
    )
