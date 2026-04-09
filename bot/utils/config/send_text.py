from typing import Any, Literal

from aiogram.types import LinkPreviewOptions
from pydantic import BaseModel, ConfigDict, PrivateAttr


class LinkPreviewConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_disabled: bool | None = None
    url: str | None = None
    media_size: Literal["large", "small"] | None = None
    show_above_text: bool | None = None

    def to_options(self) -> LinkPreviewOptions:
        data: dict[str, Any] = {}

        if self.is_disabled is not None:
            data["is_disabled"] = self.is_disabled
        if self.url is not None:
            data["url"] = self.url
        if self.show_above_text is not None:
            data["show_above_text"] = self.show_above_text
        if self.media_size == "large":
            data["prefer_large_media"] = True
        elif self.media_size == "small":
            data["prefer_small_media"] = True

        return LinkPreviewOptions(**data)


class SendText(BaseModel):
    text: str
    link_preview_options: LinkPreviewOptions | None = None

    _has_local_link_preview: bool = PrivateAttr(default=False)

    @classmethod
    def from_config(cls, value: Any) -> "SendText":
        if isinstance(value, str):
            return cls(text=value)

        if not isinstance(value, dict):
            raise ValueError("Text field must be a string or a dict")

        allowed_fields = {"text", "link_preview"}
        unexpected_fields = set(value) - allowed_fields
        if unexpected_fields:
            fields_str = ", ".join(sorted(unexpected_fields))
            raise ValueError(f"Unexpected fields for text object: {fields_str}")

        text = value.get("text")
        if not isinstance(text, str):
            raise ValueError("Text object must contain 'text' as a string")

        has_local_link_preview = "link_preview" in value
        link_preview = (
            parse_link_preview(value.get("link_preview"))
            if has_local_link_preview
            else None
        )

        response = cls(text=text, link_preview_options=link_preview)
        response._has_local_link_preview = has_local_link_preview

        return response

    def apply_global_link_preview(self, global_link_preview: LinkPreviewOptions | None):
        if self._has_local_link_preview:
            return
        self.link_preview_options = global_link_preview


def parse_link_preview(value: Any) -> LinkPreviewOptions | None:
    if value is None:
        return None

    if isinstance(value, bool):
        return LinkPreviewOptions(is_disabled=not value)

    if not isinstance(value, dict):
        raise ValueError("link_preview must be bool, null, or a dict")

    return LinkPreviewConfig.model_validate(value).to_options()
