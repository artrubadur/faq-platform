from pathlib import Path

from pydantic_settings import SettingsConfigDict

from app.core.config import config
from app.utils.config import DynamicSettings

CONSTANTS_PATH = (
    Path.cwd()
    / "config"
    / (f"constants.{config.constants}.yml" if config.constants else "constants.yml")
)

BOT_SYSTEM_KEYS = [
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


class CustomConstants(DynamicSettings):
    model_config = SettingsConfigDict(yaml_file=CONSTANTS_PATH)


constants = CustomConstants(reserved=BOT_SYSTEM_KEYS)


status = "Failed to check the status of constants"
if not CONSTANTS_PATH.exists():
    status = f"No constanst loaded: File {str(CONSTANTS_PATH)} does not exists."
elif len(constants.model_fields_set) == 1:  # reserved
    status = f"No constanst loaded: File {str(CONSTANTS_PATH)} is empty."
else:
    status = f"Constants has been loaded from {str(CONSTANTS_PATH)}"
