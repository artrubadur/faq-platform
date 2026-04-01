from pydantic import BaseModel, ConfigDict, model_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)
from pydantic_settings_yaml import YamlBaseSettings

PYDANTIC_SYSTEM_KEYS = set(dir(BaseModel))


class YamlSettings(YamlBaseSettings):
    model_config = SettingsConfigDict(secrets_dir=None, yaml_file_encoding="utf-8")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        **kwargs,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (init_settings, YamlConfigSettingsSource(settings_cls))


class DeepConvertMixin(BaseModel):
    reserved: list[str] = []

    @model_validator(mode="after")
    def deep_convert(self) -> "DeepConvertMixin":
        reserved = PYDANTIC_SYSTEM_KEYS.union(self.reserved, {"reserved"})

        for key, value in self.__pydantic_extra__.items():
            if key in reserved:
                raise ValueError(f"The key '{key}' is reserved by the system")

            if isinstance(value, dict):
                setattr(
                    self,
                    key,
                    DynamicNode(**value),
                )
        return self


class DynamicNode(DeepConvertMixin):
    model_config = ConfigDict(extra="allow")


class DynamicSettings(YamlSettings, DeepConvertMixin):
    model_config = SettingsConfigDict(extra="allow")
