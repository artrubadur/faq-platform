from aiogram.types import InlineKeyboardMarkup, Message

import app.dialogs.markups.question as qmu
import app.dialogs.markups.user as umu
import app.dialogs.rows.base as brows
import app.dialogs.rows.settings as srows
from app.core.constants.emoji import EmojiMenu
from app.dialogs.actions import SendAction, do_action


async def send_settings_menu(message: Message, *, action: SendAction):
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=srows.section_rows() + brows.close_row()
    )

    await do_action(
        message,
        action,
        text=f"{EmojiMenu.SETTINGS} Settings",
        reply_markup=reply_markup,
    )


async def send_users_menu(message: Message, *, action: SendAction):
    await do_action(
        message,
        action,
        text=f"{EmojiMenu.USERS} User Management",
        reply_markup=umu.main,
    )


async def send_questions_menu(message: Message, *, action: SendAction):
    await do_action(
        message,
        action,
        text=f"{EmojiMenu.QUESTIONS} Question Management",
        reply_markup=qmu.main,
    )
