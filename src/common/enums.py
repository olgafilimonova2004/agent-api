from enum import Enum


class RoutersMetainfo(Enum):
    DEFAULT_TAGS: list[str] = ["default"]
    DEFAULT_PREFIX: str = "/api/v1"