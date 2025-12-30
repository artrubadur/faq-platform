from typing import Optional

from app.core.constants.emoji import EmojiStatus, EmojiSymbol


def format_id(id: int):
    return f"<code>{id}</code>"


def format_user_link(id: int, username: Optional[str]):
    return f"<a href='tg://user?id={id}'>@{username or "N/A"}</a>"


def format_username(username: Optional[str]):
    return f"<code>{username or "N/A"}</code>"


def format_user_role(role: str):
    return f"<b>{role.upper()}</b>"


def format_user_output(
    id: int, username: Optional[str] = None, role: Optional[str] = None
) -> str:
    rows = [f"Link: {format_user_link(id, username)}", f"ID: {format_id(id)}"]

    if username is not None:
        rows.append(f"Username: {format_username(username)}")
    if role is not None:
        rows.append(f"Role: {format_user_role(role)}")

    return "\n".join(rows)


def format_edited_user_output(
    id: int,
    edited_id: int,
    username: Optional[str],
    edited_username: Optional[str],
    role: str,
    edited_role: str,
):
    is_id_changed = id != edited_id
    is_username_changed = username != edited_username
    is_role_changed = role != edited_role

    return (
        f"ID: {format_id(id)}{f" {EmojiSymbol.CHANGE} {format_id(edited_id)}" if is_id_changed else ""}\n"
        f"Username: {format_username(username)}{f" {EmojiSymbol.CHANGE} {format_username(edited_username)}" if is_username_changed else ""}\n"
        f"Role: {format_user_role(role)}{f" {EmojiSymbol.CHANGE} {format_user_role(edited_role)}" if is_role_changed else ""}"
    )


def format_exception_output(exception: Optional[str] = None):
    return f"{EmojiStatus.FAILED} {exception or ""}."


def format_question_output(
    id: int | None = None,
    question_text: str | None = None,
    answer_text: str | None = None,
) -> str:
    rows = []

    if id is not None:
        rows.append(f"{EmojiSymbol.NUMBER}{format_id(id)}")
    if question_text is not None:
        rows.append(f"Question: {question_text}")
    if answer_text is not None:
        rows.append(f"Answer: {answer_text}")

    return "\n".join(rows)
