from enum import Enum
from typing import List

from pydantic import BaseModel, Field, field_validator


class GraphIntent(str, Enum):
    NONE = "NONE"
    RELATIONSHIP = "RELATIONSHIP"
    LOCATION = "LOCATION"
    OWNERSHIP = "OWNERSHIP"
    MEMBERSHIP = "MEMBERSHIP"
    CAUSALITY = "CAUSALITY"
    ALL = "ALL"


class GraphQuerySpec(BaseModel):
    graph_intent: GraphIntent
    edge_types: List[str] = Field(default_factory=list)
    reason: str = ""

    @field_validator("edge_types", mode="before")
    @classmethod
    def normalize_edge_types(cls, value: List[str]) -> List[str]:
        if not value:
            return []
        return [item.strip().upper() for item in value if item.strip()]
