from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ChecklistAnswer(BaseModel):
    key: str = Field(min_length=1)
    title: str = Field(min_length=1)
    is_required: bool
    value: str | None = None


class UserChecklist(BaseModel):
    model_config = ConfigDict(extra="allow")

    incident_id: UUID
    user_id: UUID
    maxapi_id: int
    checklist_id: UUID
    checklist_type: Literal["error", "improvement", "methodological", "technical"]
    checklist_title: str
    component: str
    answers: list[ChecklistAnswer] = Field(min_length=1)
    is_ready: bool

    @model_validator(mode="after")
    def unique_keys(self) -> "UserChecklist":
        keys = [answer.key for answer in self.answers]
        if len(keys) != len(set(keys)):
            raise ValueError("answers must have unique keys")
        return self
