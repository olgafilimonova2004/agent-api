import json

import httpx

from src.models.config import LMConfig
from src.models.pydantic.checklist import UserChecklist


class LMError(Exception):
    pass


class LMClient:
    def __init__(self, config: LMConfig, session: httpx.AsyncClient | None = None):
        self.config = config
        self.session = session or httpx.AsyncClient(timeout=config.timeout_seconds)

    async def validate(self, checklist: UserChecklist) -> list[str]:
        headers = (
            {"Authorization": f"Bearer {self.config.api_key}"}
            if self.config.api_key
            else {}
        )
        payload = {
            "model": self.config.model,
            "temperature": 0,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Ты проверяешь заполненный чеклист на русском языке. "
                        "Для каждого ответа сопоставь key и title со значением value. "
                        "Верни ключи ответов, которые бессмысленны, не соответствуют полю, "
                        "содержат шаблонный текст или недостаточно конкретны для содержательного поля. "
                        "Короткие значения допустимы для версий, ролей и других справочных полей. "
                        "Пустые необязательные поля пропускай; пустые обязательные включай. "
                        "Ответь только JSON-массивом строк с key, без markdown и пояснений."
                        "Пример: [\"description\", \"contour\"]"
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        checklist.model_dump(mode="json"), ensure_ascii=False
                    ),
                },
            ],
        }
        try:
            response = await self.session.post(
                f"{str(self.config.base_url).rstrip('/')}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            result = json.loads(content)
        except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as exc:
            raise LMError(
                "LM request failed or returned an invalid response"
            ) from exc
        if not isinstance(result, list) or any(
            not isinstance(key, str) for key in result
        ):
            raise LMError("LM returned an invalid key list")
        if not set(result).issubset({answer.key for answer in checklist.answers}):
            raise LMError("LM returned unknown keys")
        return result

    async def close(self) -> None:
        await self.session.aclose()
