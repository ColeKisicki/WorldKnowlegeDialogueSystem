from dataclasses import dataclass, field
from typing import List, Dict


@dataclass(frozen=True)
class Entity:
    entity_id: str
    name: str
    type: str
    aliases: List[str] = field(default_factory=list)
    description: str = ""
    relationships: List[Dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True)
class Fact:
    fact_id: str
    entity_id: str
    type: str
    text: str
    source: str
    tags: List[str] = field(default_factory=list)
