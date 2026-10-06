from src.models.pydantic.checklist import UserChecklist
from src.models.pydantic.confluence import QUESTION_KEYS, ConfluenceRawRequest
from src.models.pydantic.search import ChecklistValidationResponse
from src.services.checklist import ChecklistService
from src.services.confluence import ConfluenceService


class ChecklistSearchService:
    def __init__(self, validator: ChecklistService, confluence: ConfluenceService):
        self.validator = validator
        self.confluence = confluence

    async def validate(self, checklist: UserChecklist) -> ChecklistValidationResponse:
        invalid_fields = await self.validator.validate(checklist)
        values = {answer.key: answer.value for answer in checklist.answers}
        for key in QUESTION_KEYS[checklist.checklist_type]:
            if not (values.get(key) or "").strip() and key not in invalid_fields:
                invalid_fields.append(key)
        if invalid_fields:
            return ChecklistValidationResponse(invalid_fields=invalid_fields)
        request = ConfluenceRawRequest.model_validate(checklist.model_dump())
        return ChecklistValidationResponse(search=await self.confluence.search(request))
