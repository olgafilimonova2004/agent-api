import os

from pydantic import BaseModel, Field

class PostgresConfig(BaseModel):
    DSN: str = Field(default="postgres://local:local@db:5432/local")
    MIN_SIZE: int = Field(default=1)
    MAX_SIZE: int = Field(default=100)
    MAX_CONN_ATTEMPT: int = Field(default=5)


class AppConfig(BaseModel):
    postgres_config: PostgresConfig

    @classmethod
    def initialize(cls):
        envs = os.environ

        postgres_config = PostgresConfig(**envs)

        return AppConfig(
            postgres_config=postgres_config
        )

