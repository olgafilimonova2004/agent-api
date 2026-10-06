from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class LMConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LM_")

    base_url: AnyHttpUrl
    model: str = Field(default="Qwen3.8-27B")
    api_key: str | None = None
    timeout_seconds: float = Field(default=30, gt=0)


class EmbedderConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="EMBEDDER_")

    base_url: AnyHttpUrl = AnyHttpUrl("http://embedder:8000/v1")
    model: str = ""
    api_key: SecretStr | None = None
    prefix: str = ""
    timeout_seconds: float = Field(default=120, gt=0)


class VespaConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="VESPA_")

    url: AnyHttpUrl = AnyHttpUrl("http://vespa:8080")
    timeout_seconds: float = Field(default=30, gt=0)


class SearchConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SEARCH_")

    confluence_threshold: float = Field(default=0.8, ge=0)
    jira_threshold: float = Field(default=0.8, ge=0)


class AppConfig(BaseSettings):
    lm: LMConfig = Field(default_factory=LMConfig)
    embedder: EmbedderConfig = Field(default_factory=EmbedderConfig)
    vespa: VespaConfig = Field(default_factory=VespaConfig)
    search: SearchConfig = Field(default_factory=SearchConfig)
