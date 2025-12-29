from enum import StrEnum


class EmojiNav(StrEnum):
    BACK = "◀️"
    CANCEL = "✖️"
    CANCEL_CHANGES = "🚫"
    REJECT = "❌"


class EmojiAction(StrEnum):
    CREATE = "➕"
    GET = "🔍"
    UPDATE = "🔧"
    DELETE = "🗑️"
    SAVE = "💾"
    ENTER = "📝"
    SELECT = "⏩"
    CLEAR = "🧹"


class EmojiStatus(StrEnum):
    CONFIRM = "✅"
    SUCCESSFUL = "✅"
    FAILED = "❌"
    WARNING = "⚠"
