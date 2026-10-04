from enum import Enum


class RoutersMetainfo(Enum):
    DEFAULT_PREFIX = "/api/v1"
    CHECKLIST_TAGS = ("checklists",)
    HEALTH_TAGS = ("health",)
    CONFLUENCE_TAGS = ("confluence",)
    JIRA_TAGS = ("jira",)
