from typing import Awaitable, Callable

from aiogram.types import InlineKeyboardMarkup, Message

import app.dialogs.markups.question as qmu
import app.dialogs.markups.user as umu
import app.dialogs.rows.common as brows
import app.dialogs.rows.settings as srows
from app.core.customization import messages
from app.dialogs.actions import with_message_action


@with_message_action
async def send_settings_menu(send: Callable[..., Awaitable[Message]]) -> Message:
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=srows.section_rows() + brows.close_row()
    )

    return await send(
        text=messages.responses.admin.settings.main,
        parse_mode=messages.parse_mode,
        reply_markup=reply_markup,
    )


@with_message_action
async def send_users_menu(
    send: Callable[..., Awaitable[Message]],
) -> Message:
    return await send(
        text=messages.responses.admin.settings.user,
        parse_mode=messages.parse_mode,
        reply_markup=umu.main,
    )


@with_message_action
async def send_questions_menu(
    send: Callable[..., Awaitable[Message]],
) -> Message:
    return await send(
        text=messages.responses.admin.settings.question,
        parse_mode=messages.parse_mode,
        reply_markup=qmu.main,
    )
