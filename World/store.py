import json
import os
import re
from typing import Dict, List, Optional

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

from World.models import Entity, Fact


class WorldKnowledgeStore:
    """
    World knowledge store backed by a Chroma vector DB.
    Loads entities and facts from JSON and supports semantic search.
    """

    def __init__(self, data_path: str, persist_dir: str):
        self.data_path = data_path
        self.persist_dir = persist_dir
        self.entities: Dict[str, Entity] = {}
        self.facts: Dict[str, Fact] = {}
        self._alias_patterns: Dict[str, re.Pattern] = {}

        self._load_data()

        self._client = chromadb.PersistentClient(path=self.persist_dir)
        self._embedding_fn = DefaultEmbeddingFunction()
        self._collection = self._client.get_or_create_collection(
            name="world_facts",
            embedding_function=self._embedding_fn,
        )

    def _load_data(self) -> None:
        with open(self.data_path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        for raw_entity in payload.get("entities", []):
            entity = Entity(
                entity_id=raw_entity["id"],
                name=raw_entity["name"],
                type=raw_entity.get("type", "unknown"),
                aliases=raw_entity.get("aliases", []),
                description=raw_entity.get("description", ""),
                relationships=raw_entity.get("relationships", []),
            )
            self.entities[entity.entity_id] = entity

        for raw_fact in payload.get("facts", []):
            fact = Fact(
                fact_id=raw_fact["id"],
                entity_id=raw_fact["entity_id"],
                type=raw_fact.get("type", "fact"),
                text=raw_fact["text"],
                source=raw_fact.get("source", "unknown"),
                tags=raw_fact.get("tags", []),
            )
            self.facts[fact.fact_id] = fact

        self._build_alias_patterns()

    def _build_alias_patterns(self) -> None:
        for entity in self.entities.values():
            aliases = [entity.name] + list(entity.aliases or [])
            for alias in aliases:
                key = f"{entity.entity_id}:{alias}".lower()
                self._alias_patterns[key] = re.compile(
                    rf"\\b{re.escape(alias)}\\b", re.IGNORECASE
                )

    def resolve_entity_ids(self, names: List[str]) -> List[str]:
        if not names:
            return []
        lookup = {}
        for entity in self.entities.values():
            for alias in [entity.name] + list(entity.aliases or []):
                lookup[alias.lower()] = entity.entity_id

        resolved = []
        for name in names:
            entity_id = lookup.get(name.strip().lower())
            if entity_id:
                resolved.append(entity_id)
        return resolved

    def world_hints(self) -> Dict[str, List[str]]:
        org_names = []
        location_names = []
        npc_names = []
        item_names = []

        for entity in self.entities.values():
            if entity.type.lower() in {"org", "organization", "faction", "guild"}:
                org_names.append(entity.name)
            elif entity.type.lower() in {"location", "place", "region", "city"}:
                location_names.append(entity.name)
            elif entity.type.lower() in {"person", "npc", "character"}:
                npc_names.append(entity.name)
            elif entity.type.lower() in {"item", "artifact", "object"}:
                item_names.append(entity.name)

        return {
            "org_names": org_names,
            "location_names": location_names,
            "npc_names": npc_names,
            "item_names": item_names,
        }

    def build_index(self, reset: bool = False) -> None:
        if reset:
            self._client.delete_collection("world_facts")
            self._collection = self._client.get_or_create_collection(
                name="world_facts",
                embedding_function=self._embedding_fn,
            )

        existing_count = self._collection.count()
        if existing_count > 0:
            return

        ids = []
        documents = []
        metadatas = []

        for fact in self.facts.values():
            entity = self.entities.get(fact.entity_id)
            entity_name = entity.name if entity else "unknown"

            ids.append(fact.fact_id)
            documents.append(f"{entity_name}: {fact.text}")
            metadatas.append(
                {
                    "entity_id": fact.entity_id,
                    "entity_name": entity_name,
                    "type": fact.type,
                    "source": fact.source,
                    "tags": ",".join(fact.tags),
                }
            )

        if ids:
            self._collection.add(ids=ids, documents=documents, metadatas=metadatas)

    def search(self, query: str, n_results: int = 5) -> List[Dict[str, str]]:
        if not query.strip():
            return []

        results = self._collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        hits = []
        for idx, fact_id in enumerate(results["ids"][0]):
            hits.append(
                {
                    "id": fact_id,
                    "text": results["documents"][0][idx],
                    "entity_id": results["metadatas"][0][idx]["entity_id"],
                    "entity_name": results["metadatas"][0][idx]["entity_name"],
                    "type": results["metadatas"][0][idx]["type"],
                    "source": results["metadatas"][0][idx]["source"],
                    "tags": results["metadatas"][0][idx]["tags"],
                    "score": str(results["distances"][0][idx]),
                }
            )

        return hits

    def find_entity_mentions(self, text: str) -> List[str]:
        if not text.strip():
            return []

        mentions = set()
        for key, pattern in self._alias_patterns.items():
            entity_id, _alias = key.split(":", 1)
            if pattern.search(text):
                mentions.add(entity_id)

        return list(mentions)

    def facts_for_entity(self, entity_id: str, limit: int = 3) -> List[Dict[str, str]]:
        facts = []
        for fact in self.facts.values():
            if fact.entity_id != entity_id:
                continue
            entity = self.entities.get(fact.entity_id)
            entity_name = entity.name if entity else "unknown"
            facts.append(
                {
                    "id": fact.fact_id,
                    "text": f"{entity_name}: {fact.text}",
                    "entity_id": fact.entity_id,
                    "entity_name": entity_name,
                    "type": fact.type,
                    "source": fact.source,
                    "tags": ",".join(fact.tags),
                    "score": "entity-match",
                }
            )
            if len(facts) >= limit:
                break
        return facts


_STORE_INSTANCE: Optional[WorldKnowledgeStore] = None


def get_world_store(reset_index: bool = False) -> WorldKnowledgeStore:
    global _STORE_INSTANCE
    if _STORE_INSTANCE is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "data", "world_facts.json")
        persist_dir = os.path.join(base_dir, "chroma")
        _STORE_INSTANCE = WorldKnowledgeStore(data_path, persist_dir)
        _STORE_INSTANCE.build_index(reset=reset_index)
    return _STORE_INSTANCE
