from pathlib import Path
from typing import Any, Literal

from aiogram.types import LinkPreviewOptions
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import SettingsConfigDict

from bot.core.customization.constants import constants
from bot.utils.config.formatter import SafeFormatter
from bot.utils.config.send_text import SendText, parse_link_preview
from shared.utils.config import YamlSettings

_MESSAGES_PATH = Path("config/messages.yml")


# Responses
class PublicRsp(BaseModel):
    start: SendText = Field(
        default_factory=lambda: SendText(
            text=(
                "Hello, {first_name}! I will help you find the answer — just send a "
                "question or choose one of the most popular ones below!"
            )
        )
    )
    failed: SendText = Field(
        default_factory=lambda: SendText(
            text="{exception}. Try to reformulate it and ask again"
        )
    )
    error: SendText = Field(
        default_factory=lambda: SendText(
            text="❌ Unexcepted internal error! We are already fixing it. Try to retry"
        )
    )
    banned: SendText = Field(
        default_factory=lambda: SendText(
            text=(
                "❌ You have been added to the blacklist and can no longer use this bot."
            )
        )
    )
    rate_limited: SendText = Field(
        default_factory=lambda: SendText(
            text="Too many requests. Please try again a bit later."
        )
    )


class UserAdmEnterRsp(BaseModel):
    identity: str = "📝 Enter the telegram id, share contact or forward a message"
    username: str = "📝 Enter a username"
    role: str = "⏩ Select a role:"


class CreationUsrAdmRsp(BaseModel):
    confirm: str = "⏩ Confirm creation?\n" "{user}"
    successful: str = "✅ User has been successfully created:\n" "{user}"
    access_denied: str = "You can’t create an admin user."


class FindingUsrAdmRsp(BaseModel):
    successful: str = (
        "✅ The user has been successfully found in the database:\n" "{user}"
    )
    partially_found: str = (
        "⚠ The user has been partially found but missing in the database:\n" "{user}"
    )


class UpdateUsrAdmRsp(BaseModel):
    confirm: str = "⏩ Update this user?\n" "{user}"
    select_field: str = "{user}\n" "⏩ Select the field to edit:"
    successful: str = "✅ The user has been successfully updated:\n" "{user}"
    access_denied: str = "You can’t update an admin user."


class DeletionUsrAdmRsp(BaseModel):
    confirm: str = "⏩ Confirm deletion?\n" "{user}"
    successful: str = "✅ Next user has been successfully deleted:\n" "{user}"
    access_denied: str = "You can’t delete an admin user."


class ListingUsrAdmRsp(BaseModel):
    successful: str = "🗂 User list: {page}/{max_page}\n" "<pre>{content}</pre>"
    not_found: str = "🗂 No users found in the system"


class UserAdmRsp(BaseModel):
    enter: UserAdmEnterRsp = Field(default_factory=UserAdmEnterRsp)
    creation: CreationUsrAdmRsp = Field(default_factory=CreationUsrAdmRsp)
    finding: FindingUsrAdmRsp = Field(default_factory=FindingUsrAdmRsp)
    update: UpdateUsrAdmRsp = Field(default_factory=UpdateUsrAdmRsp)
    deletion: DeletionUsrAdmRsp = Field(default_factory=DeletionUsrAdmRsp)
    listing: ListingUsrAdmRsp = Field(default_factory=ListingUsrAdmRsp)


class EnterQstAdmRsp(BaseModel):
    id: str = "📝 Enter the question id"
    question_text: str = "📝 Enter the question text"
    answer_text: str = "📝 Enter the answer text"
    rating: str = "📝 Enter the rating"


class CreationQstAdmRsp(BaseModel):
    confirm: str = "⏩ Confirm creation?\n {question}"
    successful: str = "✅ Question has been successfully created:\n" "{question}"
    similar: str = (
        "⚠ A similar question already exists:\n" "{question}\n" "⏩ Confirm creation?"
    )


class DeletionQstAdmRsp(BaseModel):
    confirm: str = "⏩ Confirm deletion?\n" "{question}"
    successful: str = "✅ Next question has been successfully deleted:\n" "{question}"


class UpdateQstAdmRsp(BaseModel):
    confirm: str = "⏩ Update this question?\n" "{question}"
    select_field: str = "{question}\n" "⏩ Select the field to edit:"
    confirm_recompute: str = "⏩ Recompute embedding?"
    successful: str = "✅ The question has been successfully updated:\n" "{question}"


class FindingQstAdmRsp(BaseModel):
    successful: str = "✅ The question has been successfully found:\n" "{question}"


class ListingQstAdmRsp(BaseModel):
    successful: str = "🗂 Question list: {page}/{max_page}\n" "<pre>{content}</pre>"
    not_found: str = "🗂 No questions found in the system"


class QuestionAdmRsp(BaseModel):
    enter: EnterQstAdmRsp = Field(default_factory=EnterQstAdmRsp)
    creation: CreationQstAdmRsp = Field(default_factory=CreationQstAdmRsp)
    deletion: DeletionQstAdmRsp = Field(default_factory=DeletionQstAdmRsp)
    update: UpdateQstAdmRsp = Field(default_factory=UpdateQstAdmRsp)
    finding: FindingQstAdmRsp = Field(default_factory=FindingQstAdmRsp)
    listing: ListingQstAdmRsp = Field(default_factory=ListingQstAdmRsp)


class SettingsAdmRsp(BaseModel):
    main: str = "⚙ Settings"
    user: str = "👤 User"
    question: str = "📚 Question"


class GotoMscAdmRsp(BaseModel):
    go: str = "Go!"
    confirm: str = "⏩ Go to <code>{content}<code>?"


class StateMscAdmRsp(BaseModel):
    serialization: str = '<pre><code class="json">{content}</code></pre>'
    argument: str = "<code>{content}</code>"


class MiscAdmRsp(BaseModel):
    goto: GotoMscAdmRsp = Field(default_factory=GotoMscAdmRsp)
    state: StateMscAdmRsp = Field(default_factory=StateMscAdmRsp)


class BanAdmRsp(BaseModel):
    banned: str = "✅ User {identity} has been banned."
    unbanned: str = "✅ User {identity} has been unbanned."


class AdminRsp(BaseModel):
    invalid: str = "⚠ {exception}. Retry or back"
    expired: str = "The time for the operation has expired. Start over"
    access_denied: str = "Access denied: {exception}"
    user: UserAdmRsp = Field(default_factory=UserAdmRsp)
    question: QuestionAdmRsp = Field(default_factory=QuestionAdmRsp)
    settings: SettingsAdmRsp = Field(default_factory=SettingsAdmRsp)
    misc: MiscAdmRsp = Field(default_factory=MiscAdmRsp)
    ban: BanAdmRsp = Field(default_factory=BanAdmRsp)


class Responses(BaseModel):
    public: PublicRsp = Field(default_factory=PublicRsp)
    admin: AdminRsp = Field(default_factory=AdminRsp)


# Exception


class SearchExc(BaseModel):
    not_found: str = "It seems that we failed to understand the question"


class UserExc(BaseModel):
    not_found: str = "User {identity} not found"
    already_exists: str = (
        "A user with the ID {id} or the username {username} already exists"
    )


class QuestionExc(BaseModel):
    not_found: str = "Question {id} not found"
    embedding_failed: str = "Failed to compute vector representation of question"


class MiscExc(BaseModel):
    invalid_changes: str = "Pass changes with the <code>key=value</code> format"
    invalid_argument: str = "Invalid argument: {exception}"
    invalid_path: str = "Failed to go: The path is not set"


class Exceptions(BaseModel):
    search: SearchExc = Field(default_factory=SearchExc)
    user: UserExc = Field(default_factory=UserExc)
    question: QuestionExc = Field(default_factory=QuestionExc)
    misc: MiscExc = Field(default_factory=MiscExc)


# Process


class CommonPrc(BaseModel):
    page_invalid: str = "Message type is invalid"


class UserPrc(BaseModel):
    contact_invalid: str = "The account is hidden or the user is not registered"
    identity_invalid: str = (
        "Please send a simple text message with ID, contact or forward the message"
    )
    username_invalid: str = "Please send a simple text message with the username"
    role_invalid: str = (
        "Please send a simple text message with the role or choose one from the list"
    )


class QuestionPrc(BaseModel):
    id_invalid: str = "Please send a simple text message with ID"
    msg_question_text_invalid: str = (
        "Please send a simple text message with the question"
    )
    cmd_question_text_invalid: str = (
        "Please specify the question text after the command"
    )
    answer_text_invalid: str = (
        "Please send a simple text message with the answer to the question"
    )
    rating_invalid: str = "Please send a simple text message with the rating"


class Process(BaseModel):
    common: CommonPrc = Field(default_factory=CommonPrc)
    user: UserPrc = Field(default_factory=UserPrc)
    question: QuestionPrc = Field(default_factory=QuestionPrc)


# Validation


class CommonVal(BaseModel):
    page_invalid: str = "Page is invalid"
    page_negative: str = "Page cannot be negative"


class UserVal(BaseModel):
    id_invalid: str = "ID is invalid"
    username_short: str = "The username is too short"
    username_long: str = "The username is too long"
    username_unexcepted_symbols: str = "The username has unexcepted symbols"
    role_unexcepted: str = "An unexpected role"


class QuestionVal(BaseModel):
    id_invalid: str = "ID is invalid"
    question_text_long: str = "The question text is too long"
    answer_text_long: str = "The answer text is too long"
    rating_incorrect: str = "Rating is incorrect"


class Validation(BaseModel):
    common: CommonVal = Field(default_factory=CommonVal)
    user: UserVal = Field(default_factory=UserVal)
    question: QuestionVal = Field(default_factory=QuestionVal)


# Settings


class QuestionSet(BaseModel):
    question_text: str = "Question Text"
    answer_text: str = "Answer Text"
    rating: str = "Rating"

    found: str = "Found ({id})"


class UserSet(BaseModel):
    username: str = "Username"
    role: str = "Role"

    found: str = "Found ({identity})"
    you: str = "You ({identity})"


class SettingsSet(BaseModel):
    user: str = "👤 Users"
    question: str = "📚 Questions"


class CommonSet(BaseModel):
    close: str = "✖️ Close"
    back: str = "◀️ Back"
    cancel: str = "✖️ Cancel"
    create: str = "➕ Create"
    get: str = "🔍 Get"
    update: str = "🔧 Update"
    delete: str = "🗑️ Delete"
    list: str = "🗂 List"
    confirm: str = "✅"
    reject: str = "❌"
    previous: str = "◀️"
    next: str = "▶️"
    save: str = "💾"
    discard: str = "✖️"
    ascending: str = "🔼"
    descending: str = "🔽"
    empty: str = "🧹 Empty"


class Button(BaseModel):
    question: QuestionSet = Field(default_factory=QuestionSet)
    user: UserSet = Field(default_factory=UserSet)
    settings: SettingsSet = Field(default_factory=SettingsSet)
    common: CommonSet = Field(default_factory=CommonSet)


# Format


class FieldFmt(BaseModel):
    id: str = "<code>{id}</code>"
    exception: str = "❌ {exception}"

    question_text: str = "{question_text}"
    answer_text: str = "{answer_text}"
    rating: str = "{rating}"

    username: str = "<code>{username}</code>"
    user_link: str = "<a href='tg://user?id={id}'>@{username}</a>"
    user_role: str = "<b>{user_role}</b>"

    date: str = "%d.%m.%Y %H:%M"


class FallbackFmt(BaseModel):
    last_name: str = ""
    username: str = ""
    exception: str = ""


class QuestionFmt(BaseModel):
    id: str = "#️⃣ {id} Question:"
    question_text: str = "🔍 Text: {question_text}"
    answer_text: str = "💡 Answer: {answer_text}"
    rating: str = "🚀 Rating: {rating}"
    # recomputed: str = "🧬 Embedding will be recomputed"
    # not_recomputed: str = "🧬 Embedding will NOT be recomputed"


class UserFmt(BaseModel):
    id: str = "ID: {id}"
    username: str = "Username: {username}"
    user_link: str = "Link: {user_link}"
    user_role: str = "Role: {user_role}"


class EditFmt(BaseModel):
    unedited: str = "{old}"
    edited: str = "{old} ➡️ {new}"


class Format(BaseModel):
    field: FieldFmt = Field(default_factory=FieldFmt)
    fallback: FallbackFmt = Field(default_factory=FallbackFmt)
    question: QuestionFmt = Field(default_factory=QuestionFmt)
    user: UserFmt = Field(default_factory=UserFmt)
    edit: EditFmt = Field(default_factory=EditFmt)
    canceled: str = "{old}\n✖️ CANCELED ✖️"


class Messages(YamlSettings):
    model_config = SettingsConfigDict(yaml_file=_MESSAGES_PATH, frozen=False)

    parse_mode: Literal["html", "markdown", "markdownv2", None] = "html"
    link_preview: LinkPreviewOptions | None = None

    @field_validator("parse_mode", mode="before")
    def validate_parse_mode(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v

    @field_validator("link_preview", mode="before")
    def validate_link_preview(cls, v):
        return parse_link_preview(v)

    responses: Responses = Field(default_factory=Responses)

    exceptions: Exceptions = Field(default_factory=Exceptions)
    process: Process = Field(default_factory=Process)
    validation: Validation = Field(default_factory=Validation)

    button: Button = Field(default_factory=Button)
    format: Format = Field(default_factory=Format)

    @model_validator(mode="before")
    def apply_constants(cls, data: dict[str, Any]) -> dict[str, Any]:
        formatter = SafeFormatter()

        def _format(text: str) -> str:
            try:
                return formatter.format(text, constants=constants.constants)
            except (AttributeError, ValueError) as exc:
                raise ValueError(
                    "Attempt to access a non-existent constant in messages config"
                ) from exc

        def _apply_constants_recursive(value: Any) -> Any:
            if isinstance(value, str):
                return _format(value)

            if isinstance(value, dict):
                return {
                    field: _apply_constants_recursive(obj)
                    for field, obj in value.items()
                }

            return value

        return _apply_constants_recursive(data)

    @field_validator("responses", mode="before")
    def apply_link_preview(
        cls, responses: Responses | dict[str, Any]
    ) -> Responses | dict[str, Any]:
        if not isinstance(responses, dict):
            return responses

        public = responses.get("public")
        if not isinstance(public, dict):
            return responses

        responses["public"] = {
            field: SendText.from_config(value) for field, value in public.items()
        }
        return responses

    @model_validator(mode="after")
    def apply_default_link_preview(self) -> "Messages":
        for field in PublicRsp.model_fields:
            getattr(self.responses.public, field).apply_global_link_preview(
                self.link_preview
            )

        return self


messages: Messages = Messages()


status = "Failed to check the status of messages"
if not _MESSAGES_PATH.exists() or not _MESSAGES_PATH.is_file():
    status = f"No messages loaded: File {str(_MESSAGES_PATH)} does not exist."
elif len(messages.model_fields_set) == 0:
    status = f"No messages loaded: File {str(_MESSAGES_PATH)} is empty."
else:
    status = f"Messages have been loaded from {str(_MESSAGES_PATH)}"
