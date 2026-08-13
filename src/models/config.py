from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    DSN: str = Field(...)
    MIN_SIZE: int = Field(default=1)
    MAX_SIZE: int = Field(default=100)
    MAX_CONN_ATTEMPT: int = Field(default=5)


class AppConfig(BaseModel):
    postgres_config: PostgresConfig

    @classmethod
    def initialize(cls):
        postgres_config = PostgresConfig()

        return AppConfig(postgres_config=postgres_config)
