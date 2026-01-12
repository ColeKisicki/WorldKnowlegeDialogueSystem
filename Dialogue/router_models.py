from enum import Enum
from typing import List

from pydantic import BaseModel, Field, field_validator, model_validator


class Intent(str, Enum):
    ASK_EVENTS = "ASK_EVENTS"
    ASK_ENTITY_FACTS = "ASK_ENTITY_FACTS"
    ASK_LOCATION = "ASK_LOCATION"
    ASK_HOW_TO = "ASK_HOW_TO"
    ASK_RELATIONSHIP = "ASK_RELATIONSHIP"
    ASK_COMPARISON = "ASK_COMPARISON"
    ASK_COUNT = "ASK_COUNT"
    SMALLTALK = "SMALLTALK"
    OTHER = "OTHER"


class EntityType(str, Enum):
    NPC = "NPC"
    ORG = "ORG"
    FACTION = "FACTION"
    LOCATION = "LOCATION"
    ITEM = "ITEM"
    EVENT = "EVENT"
    UNKNOWN = "UNKNOWN"


class LocationBiasMode(str, Enum):
    NEAR_NPC = "NEAR_NPC"
    SPECIFIC_LOCATION = "SPECIFIC_LOCATION"
    NONE = "NONE"


class AnswerFormat(str, Enum):
    BRIEF = "BRIEF"
    NORMAL = "NORMAL"
    DETAILED = "DETAILED"


class ExtractedEntity(BaseModel):
    name: str
    type: EntityType = EntityType.UNKNOWN

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        return value.strip()


class LocationBias(BaseModel):
    mode: LocationBiasMode
    location_name: str = ""

    @field_validator("location_name")
    @classmethod
    def strip_location_name(cls, value: str) -> str:
        return value.strip()


class QuerySpec(BaseModel):
    intent: Intent
    query_text: str
    entities: List[ExtractedEntity] = Field(default_factory=list)
    needs_retrieval: bool = True
    time_window_days: int = 0
    time_constraint_text: str = ""
    location_bias: LocationBias
    answer_format: AnswerFormat = AnswerFormat.NORMAL

    @field_validator("query_text", "time_constraint_text")
    @classmethod
    def strip_strings(cls, value: str) -> str:
        return value.strip()

    @field_validator("time_window_days")
    @classmethod
    def clamp_time_window(cls, value: int) -> int:
        if value < 0:
            return 0
        if value > 365:
            return 365
        return value

    @model_validator(mode="after")
    def ensure_query_text(self) -> "QuerySpec":
        if not self.query_text:
            self.query_text = "unknown"
        return self
