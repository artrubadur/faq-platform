from enum import StrEnum


class EmojiMenu(StrEnum):
    SETTINGS = "⚙"
    USERS = "👤"
    QUESTIONS = "📚"


class EmojiNav(StrEnum):
    BACK = "◀️"
    CANCEL = "✖️"
    CANCEL_CHANGES = "🚫"
    REJECT = "❌"
    CLOSE = "✖️"


class EmojiAction(StrEnum):
    CREATE = "➕"
    GET = "🔍"
    UPDATE = "🔧"
    DELETE = "🗑️"
    SAVE = "💾"
    ENTER = "📝"
    SELECT = "⏩"
    EMPTY = "🧹"


class EmojiStatus(StrEnum):
    CONFIRM = "✅"
    SUCCESSFUL = "✅"
    FAILED = "❌"
    WARNING = "⚠"


class EmojiSymbol(StrEnum):
    CHANGE = "➡️"
    NUMBER = "#️⃣"
    QUESTION = "🔍"
    ANSWER = "💡"
    EMBEDDING = "🧬"
