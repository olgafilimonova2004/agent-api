from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ConfluenceRawRequest(BaseModel): # отсюда достаем и description как основной запрос, остальное - meta_info и tags
    model_config = ConfigDict(extra="ignore")

    checklist_type: Literal["error", "improvement", "methodological", "technical"]
    checklist_title: str
    component: str
    answers: list[ChecklistAnswer] = Field(min_length=1)

