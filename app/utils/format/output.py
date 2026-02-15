from enum import Enum

from app.core.constants.emojis import EmojiStatus, EmojiSymbol
from app.storage.models.question import Question
from app.storage.models.user import User


def format_exception(exception: str | None = None):
    return f"{EmojiStatus.FAILED} {exception or ""}."


def format_id(id: int):
    return f"<code>{id}</code>"


def format_user_link(id: int, username: str | None):
    return f"<a href='tg://user?id={id}'>@{username or "N/A"}</a>"


def format_username(username: str | None):
    return f"<code>{username or "N/A"}</code>"


def format_user_role(role: str):
    return f"<b>{role.upper()}</b>"


def format_user(id: int, username: str | None = None, role: str | None = None) -> str:
    result = f"Link: {format_user_link(id, username)}\nID: {format_id(id)}\n"

    if username is not None:
        result += f"Username: {format_username(username)}\n"

    if role is not None:
        result += f"Role: {format_user_role(role)}\n"

    return result


def format_edited_user(
    id: int,
    username: str | None,
    edited_username: str | None,
    role: str,
    edited_role: str,
):
    is_username_changed = username != edited_username
    is_role_changed = role != edited_role

    return format_user(
        id,
        f"{format_username(username)}{f" {EmojiSymbol.CHANGE} {format_username(edited_username)}"if is_username_changed else ""}",
        f"{format_user_role(role)}{f" {EmojiSymbol.CHANGE} {format_user_role(edited_role)}"if is_role_changed else ""}",
    )


def format_question(
    id: int | None = None,
    question_text: str | None = None,
    answer_text: str | None = None,
    rating: str | float | None = None,
) -> str:
    result = ""

    if id is not None:
        result += f"{EmojiSymbol.INDEX}{format_id(id)} Question:\n"

    if question_text is not None:
        result += f"{EmojiSymbol.QUESTION} Text:\n {question_text}\n"

    if answer_text is not None:
        result += f"{EmojiSymbol.ANSWER} Answer:\n {answer_text}\n"

    if rating is not None:
        result += f"{EmojiSymbol.RATING} Rating: {rating}\n"

    return result


def format_edited_question(
    id: int,
    question_text: str,
    edited_question_text: str,
    answer_text: str,
    edited_answer_text: str,
    rating: float,
    edited_rating: float,
    recompute_embedding: bool,
):
    is_question_text_changed = question_text != edited_question_text
    is_answer_text_changed = answer_text != edited_answer_text
    is_rating_changed = rating != edited_rating

    result = format_question(
        id,
        f"{question_text}{f" {EmojiSymbol.CHANGE}\n{edited_question_text}"if is_question_text_changed else ""}",
        f"{answer_text}{f" {EmojiSymbol.CHANGE}\n{edited_answer_text}" if is_answer_text_changed else ""}",
        f"{rating}{f" {EmojiSymbol.CHANGE} {edited_rating}" if is_rating_changed else ""}",
    )

    status = "<b>NOT</b> " if not recompute_embedding else ""
    result += f"{EmojiSymbol.EMBEDDING} Embedding will {status}be recomputed\n"

    return result


def format_user_table(rows: list[User], columns: list, idx_offset=0):
    full_headers = [""] + columns

    def extract_value(row, field):
        val = getattr(row, field, "")

        if isinstance(val, Enum):
            return val.value

        if val is None:
            return ""

        return str(val)

    table = []
    for idx, row in enumerate(rows, 1):
        row_values = [str(idx + idx_offset)]
        for col in columns:
            row_values.append(extract_value(row, col))
        table.append(row_values)

    col_count = len(full_headers)
    widths = [len(str(h)) for h in full_headers]

    for row in table:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def fmt_row(row):
        return " | ".join(row[i].ljust(widths[i]) for i in range(col_count))

    header_line = fmt_row(full_headers)
    separator = "-+-".join("-" * widths[i] for i in range(col_count))
    rows_lines = [fmt_row(r) for r in table]

    return "\n".join([header_line, separator] + rows_lines)


def format_question_table(rows: list[Question], columns: list, idx_offset=0):
    def extract_value(row, field):
        val = getattr(row, field, "")

        if isinstance(val, Enum):
            return val.value

        if val is None:
            return ""

        return str(val)

    table = []
    for idx, row in enumerate(rows, 1):
        row_values = [str(idx + idx_offset)]
        for col in columns:
            row_values.append(extract_value(row, col))
        table.append(row_values)

    def fmt_row(row):
        delimiter = f"--- Question #{row[0]} ---\n"
        card = "\n".join(f"{col}: {row[i+1]}" for i, col in enumerate(columns))
        return delimiter + card

    rows_lines = [fmt_row(r) for r in table]

    return "\n\n".join(rows_lines)
