import os

from pydantic import BaseModel, Field

class DBConfig(BaseModel):
    DB_URL: str = Field(...)


class AppConfig(BaseModel):
    db_config: DBConfig

    @classmethod
    def create(cls):
        envs = os.environ

        db_config = DBConfig(**envs)

        return AppConfig(
            db_config=db_config
        )

