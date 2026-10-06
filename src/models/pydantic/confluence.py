from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.models.pydantic.checklist import ChecklistAnswer

QUESTION_KEYS: dict[str, tuple[str, ...]] = {
    "error": ("description",),
    "technical": ("description",),
    "methodological": ("question",),
    "improvement": ("summary", "proposal"),
}


class ConfluenceRawRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    checklist_type: Literal["error", "improvement", "methodological", "technical"]
    checklist_title: str
    component: str
    answers: list[ChecklistAnswer] = Field(min_length=1)
    clarification: str | None = None

    @model_validator(mode="after")
    def validate_answers(self) -> "ConfluenceRawRequest":
        values = {answer.key: answer.value for answer in self.answers}
        if len(values) != len(self.answers):
            raise ValueError("answers must have unique keys")
        for key in QUESTION_KEYS[self.checklist_type]:
            if not (values.get(key) or "").strip():
                raise ValueError(f"answers must contain nonempty {key}")
        return self
