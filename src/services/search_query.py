from src.models.pydantic.confluence import QUESTION_KEYS, ConfluenceRawRequest


class SearchQueryBuilder:
    def construct(self, request: ConfluenceRawRequest) -> str:
        return "\n".join(
            [
                'Оператор отправил следующий вопрос о системе ПК РКМ "АРСЕНАЛ":',
                *self._content(request),
                "Найди подходящий ответ на запрос в базе знаний.",
            ]
        )

    def construct_jira(self, request: ConfluenceRawRequest) -> str:
        return "\n".join(
            [
                "Найди описание похожего запроса/проблемы:",
                *self._content(request),
            ]
        )

    def _content(self, request: ConfluenceRawRequest) -> list[str]:
        question_keys = QUESTION_KEYS[request.checklist_type]
        context = []
        content = []
        for answer in request.answers:
            value = (answer.value or "").strip()
            if not value:
                continue
            title = answer.title.replace("**", "").strip()
            if answer.key in question_keys:
                content.append(f"{title}: {value}" if len(question_keys) > 1 else value)
            else:
                context.append(f"{title}: {value}")
        clarification = (request.clarification or "").strip()
        if clarification != []:
            return [
            f"Тип вопроса: {request.checklist_title}",
            f"Компонент: {request.component}",
            *context,
            "Содержание вопроса:",
            *content,
            *(["Уточнения пользователя:", clarification]),
        ]
        return [
            f"Тип вопроса: {request.checklist_title}",
            f"Компонент: {request.component}",
            *context,
            "Содержание вопроса:",
            *content
        ]
