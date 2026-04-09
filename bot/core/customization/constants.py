from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import SettingsConfigDict

from shared.utils.config import DynamicNode, YamlSettings

_CONSTANTS_PATH = Path("config/constants.yml")


class CustomConstants(YamlSettings):
    model_config = SettingsConfigDict(yaml_file=_CONSTANTS_PATH, extra="forbid")
    constants: DynamicNode = Field(default_factory=DynamicNode)


constants = CustomConstants()


status = "Failed to check the status of constants"
if not _CONSTANTS_PATH.exists() or not _CONSTANTS_PATH.is_file():
    status = f"No constants loaded: File {str(_CONSTANTS_PATH)} does not exist."
elif not constants.constants.model_extra:
    status = f"No constants loaded: File {str(_CONSTANTS_PATH)} is empty."
else:
    status = f"Constants have been loaded from {str(_CONSTANTS_PATH)}"
