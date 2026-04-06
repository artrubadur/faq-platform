from pathlib import Path

from pydantic_settings import SettingsConfigDict

from shared.utils.config import DynamicSettings

_BOT_SYSTEM_KEYS = [
    "identity",
    "id",
    "user",
    "first_name",
    "last_name",
    "username",
    "full_name",
    "date",
    "user_link",
    "user_role",
    "question",
    "question_text",
    "answer_text",
    "rating",
    "old",
    "new",
    "page",
    "max_page",
    "content",
    "exception",
]
_CONSTANTS_PATH = Path("config/constants.yml")


class CustomConstants(DynamicSettings):
    model_config = SettingsConfigDict(yaml_file=_CONSTANTS_PATH)


constants = CustomConstants(reserved=_BOT_SYSTEM_KEYS)


status = "Failed to check the status of constants"
if not _CONSTANTS_PATH.exists() or not _CONSTANTS_PATH.is_file():
    status = f"No constants loaded: File {str(_CONSTANTS_PATH)} does not exist."
elif len(constants.model_fields_set) == 1:  # reserved
    status = f"No constants loaded: File {str(_CONSTANTS_PATH)} is empty."
else:
    status = f"Constants have been loaded from {str(_CONSTANTS_PATH)}"
