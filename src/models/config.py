from pydantic import AnyUrl, BaseModel, Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    DSN: PostgresDsn = Field(...)
    MIN_SIZE: int = Field(default=1)
    MAX_SIZE: int = Field(default=100)
    MAX_CONN_ATTEMPT: int = Field(default=5)


class BaseClientConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CLIENT_")
    BASE_URL: AnyUrl = Field(
        ..., description="BASE URL API, к которому обращается клиент"
    )


class AppConfig(BaseModel):
    postgres_config: PostgresConfig
    client: BaseClientConfig

    @classmethod
    def initialize(cls):
        postgres_config = PostgresConfig()
        client_config = BaseClientConfig()

        return AppConfig(postgres_config=postgres_config, client=client_config)
