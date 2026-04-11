from enum import Enum

from aiogram.types import Message

from bot.core.customization import messages
from shared.contracts.formulation.responses import FormulationResponse
from shared.contracts.question.responses import QuestionResponse
from shared.contracts.user.responses import Role, UserResponse


def format_response(text: str, message: Message, **kwargs):
    return text.format(
        id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name or messages.format.fallback.last_name,
        username=message.from_user.username or messages.format.fallback.username,
        full_name=message.from_user.full_name,
        date=message.date.strftime(messages.format.field.date),
        **kwargs,
    )


def format_exception(exception: str | None = None, **kwargs):
    return messages.format.field.exception.format(
        exception=exception or messages.format.fallback.exception
    ).format(**kwargs)


def format_id(id: int):
    return messages.format.field.id.format(id=id)


def format_username(username: str | None):
    return messages.format.field.username.format(
        id=id, username=username or messages.format.fallback.username
    )


def format_user_link(id: int, username: str | None):
    return messages.format.field.user_link.format(
        id=id, username=username or messages.format.fallback.username
    )


def format_user_role(role: Role):
    return messages.format.field.user_role.format(user_role=role.value)


def format_question_text(question_text: str):
    return messages.format.field.question_text.format(question_text=question_text)


def format_answer_text(answer_text: str):
    return messages.format.field.answer_text.format(answer_text=answer_text)


def format_rating(rating: float | str):
    return messages.format.field.rating.format(rating=rating)


def format_user(id: int, username: str | None = None, role: Role | None = None) -> str:
    result = [
        messages.format.user.id.format(id=format_id(id)),
        messages.format.user.user_link.format(user_link=format_user_link(id, username)),
    ]

    if username is not None:
        result.append(
            messages.format.user.username.format(username=format_username(username))
        )

    if role is not None:
        result.append(
            messages.format.user.user_role.format(user_role=format_user_role(role))
        )

    return "\n".join(result)


def format_edited_user(
    id: int,
    username: str | None,
    edited_username: str | None,
    role: Role,
    edited_role: Role,
):
    is_username_changed = username != edited_username
    is_role_changed = role != edited_role

    result = [messages.format.user.id.format(id=format_id(id))]

    result += [
        messages.format.user.user_link.format(
            user_link=(
                messages.format.edit.edited.format(
                    old=format_user_link(id, username),
                    new=format_user_link(id, edited_username),
                )
                if is_username_changed
                else messages.format.edit.unedited.format(
                    old=format_user_link(id, username)
                )
            )
        )
    ]

    result += [
        messages.format.user.username.format(
            username=(
                messages.format.edit.edited.format(
                    old=format_username(username), new=format_username(edited_username)
                )
                if is_username_changed
                else messages.format.edit.unedited.format(old=format_username(username))
            )
        )
    ]

    result += [
        messages.format.user.user_role.format(
            user_role=(
                messages.format.edit.edited.format(
                    old=format_user_role(role), new=format_user_role(edited_role)
                )
                if is_role_changed
                else messages.format.edit.unedited.format(old=format_user_role(role))
            )
        )
    ]

    return "\n".join(result)


def format_question(
    id: int | None = None,
    question_text: str | None = None,
    answer_text: str | None = None,
    rating: str | float | None = None,
    formulation_ids: list[int] | None = None,
) -> str:
    result = []

    if id is not None:
        result.append(messages.format.question.id.format(id=format_id(id)))

    if question_text is not None:
        result.append(
            messages.format.question.question_text.format(
                question_text=format_question_text(question_text)
            )
        )

    if answer_text is not None:
        result.append(
            messages.format.question.answer_text.format(
                answer_text=format_answer_text(answer_text)
            )
        )

    if rating is not None:
        result.append(
            messages.format.question.rating.format(rating=format_rating(rating))
        )

    if formulation_ids is not None:
        result.append(
            messages.format.question.formulations_amount.format(
                amount=len(formulation_ids)
            )
        )
        formulation_ids_text = (
            ", ".join(format_id(formulation_id) for formulation_id in formulation_ids)
            if formulation_ids
            else "-"
        )
        result.append(
            messages.format.question.formulation_ids.format(ids=formulation_ids_text)
        )

    return "\n".join(result)


def format_formulation(
    id: int | None = None,
    question_id: int | None = None,
    question_text: str | None = None,
) -> str:
    result = []

    if id is not None:
        result.append(messages.format.formulation.id.format(id=format_id(id)))

    if question_id is not None:
        result.append(
            messages.format.formulation.question_id.format(
                question_id=format_id(question_id)
            )
        )

    if question_text is not None:
        result.append(
            messages.format.formulation.question_text.format(
                question_text=format_question_text(question_text)
            )
        )

    return "\n".join(result)


def format_edited_formulation(
    id: int,
    question_id: int,
    edited_question_id: int,
    question_text: str,
    edited_question_text: str,
    recompute_embedding: bool,
):
    is_question_id_changed = question_id != edited_question_id
    is_question_text_changed = question_text != edited_question_text

    result = [messages.format.formulation.id.format(id=format_id(id))]

    result.append(
        messages.format.formulation.question_id.format(
            question_id=(
                messages.format.edit.edited.format(
                    old=format_id(question_id),
                    new=format_id(edited_question_id),
                )
                if is_question_id_changed
                else messages.format.edit.unedited.format(old=format_id(question_id))
            )
        )
    )

    result.append(
        messages.format.formulation.question_text.format(
            question_text=(
                messages.format.edit.edited.format(
                    old=format_question_text(question_text),
                    new=format_question_text(edited_question_text),
                )
                if is_question_text_changed
                else messages.format.edit.unedited.format(
                    old=format_question_text(question_text)
                )
            )
        )
    )

    result.append(
        messages.format.formulation.recompute_embedding.format(
            recompute_embedding=(
                messages.format.formulation.recompute_true
                if recompute_embedding
                else messages.format.formulation.recompute_false
            )
        )
    )

    return "\n".join(result)


def format_edited_question(
    id: int,
    question_text: str,
    edited_question_text: str,
    answer_text: str,
    edited_answer_text: str,
    rating: float,
    edited_rating: float,
):
    is_question_text_changed = question_text != edited_question_text
    is_answer_text_changed = answer_text != edited_answer_text
    is_rating_changed = rating != edited_rating

    result = [messages.format.question.id.format(id=format_id(id))]

    result.append(
        messages.format.question.question_text.format(
            question_text=(
                messages.format.edit.edited.format(
                    old=format_question_text(question_text),
                    new=format_question_text(edited_question_text),
                )
                if is_question_text_changed
                else messages.format.edit.unedited.format(
                    old=format_question_text(question_text)
                )
            )
        )
    )

    result.append(
        messages.format.question.answer_text.format(
            answer_text=(
                messages.format.edit.edited.format(
                    old=format_answer_text(answer_text),
                    new=format_answer_text(edited_answer_text),
                )
                if is_answer_text_changed
                else messages.format.edit.unedited.format(
                    old=format_answer_text(answer_text)
                )
            )
        )
    )

    result.append(
        messages.format.question.rating.format(
            rating=(
                messages.format.edit.edited.format(
                    old=format_rating(rating), new=format_rating(edited_rating)
                )
                if is_rating_changed
                else messages.format.edit.unedited.format(old=format_rating(rating))
            )
        )
    )

    return "\n".join(result)


def format_user_table(rows: list[UserResponse], columns: list[str], idx_offset=0):
    full_headers = [""] + columns

    def extract_value(row: UserResponse, field: str):
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


def format_question_table(rows: list[QuestionResponse], columns: list, idx_offset=0):
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
        delimiter = f"----- #{row[0]} -----\n"
        card = "\n".join(f"{col}: {row[i+1]}" for i, col in enumerate(columns))
        return delimiter + card

    rows_lines = [fmt_row(r) for r in table]

    return "\n\n".join(rows_lines)


def format_formulation_table(
    rows: list[FormulationResponse], columns: list, idx_offset=0
):
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
        delimiter = f"----- #{row[0]} -----\n"
        card = "\n".join(f"{col}: {row[i+1]}" for i, col in enumerate(columns))
        return delimiter + card

    rows_lines = [fmt_row(r) for r in table]

    return "\n\n".join(rows_lines)
