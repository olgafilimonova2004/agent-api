from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LMConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LM_")

    base_url: AnyHttpUrl
    model: str = Field(default="Qwen3.8-27B")
    api_key: str | None = None
    timeout_seconds: float = Field(default=30, gt=0)


class AppConfig(BaseSettings):
    lm: LMConfig = Field(default_factory=LMConfig)
