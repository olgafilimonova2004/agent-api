from src.clients.lm_client import LMClient
from src.models.pydantic.checklist import UserChecklist


class ChecklistService:
    def __init__(self, client: LMClient):
        self.client = client

    async def validate(self, checklist: UserChecklist) -> list[str]:
        required_empty = {
            answer.key
            for answer in checklist.answers
            if answer.is_required and not (answer.value or "").strip()
        }
        model_keys = await self.client.validate(checklist)
        flagged = required_empty | set(model_keys)
        return [
            answer.key
            for answer in checklist.answers
            if answer.key in flagged
            and (answer.is_required or (answer.value or "").strip())
        ]
