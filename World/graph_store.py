import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class GraphEntity:
    entity_id: str
    name: str
    type: str
    aliases: List[str] = field(default_factory=list)
    description: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class GraphEdge:
    edge_id: str
    type: str
    source_id: str
    target_id: str
    properties: Dict[str, str] = field(default_factory=dict)


class InMemoryGraphStore:
    def __init__(self, entities_path: str, edges_path: str):
        self.entities_path = entities_path
        self.edges_path = edges_path
        self.entities: Dict[str, GraphEntity] = {}
        self.edges: List[GraphEdge] = []
        self._name_index: Dict[str, str] = {}
        self._out_edges: Dict[str, List[GraphEdge]] = {}
        self._in_edges: Dict[str, List[GraphEdge]] = {}

        self._load()
        self._build_index()

    def _load(self) -> None:
        with open(self.entities_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        for raw in payload.get("entities", []):
            entity = GraphEntity(
                entity_id=raw["id"],
                name=raw["name"],
                type=raw.get("type", "unknown"),
                aliases=raw.get("aliases", []),
                description=raw.get("description", ""),
                tags=raw.get("tags", []),
            )
            self.entities[entity.entity_id] = entity

        with open(self.edges_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        for raw in payload.get("edges", []):
            edge = GraphEdge(
                edge_id=raw["id"],
                type=raw.get("type", "RELATED_TO"),
                source_id=raw["source_id"],
                target_id=raw["target_id"],
                properties=raw.get("properties", {}),
            )
            self.edges.append(edge)

    def _build_index(self) -> None:
        for entity in self.entities.values():
            for alias in [entity.name] + list(entity.aliases):
                self._name_index[alias.lower()] = entity.entity_id

        for edge in self.edges:
            self._out_edges.setdefault(edge.source_id, []).append(edge)
            self._in_edges.setdefault(edge.target_id, []).append(edge)

    def get_entity_by_name(self, name: str) -> Optional[GraphEntity]:
        if not name:
            return None
        entity_id = self._name_index.get(name.strip().lower())
        if not entity_id:
            return None
        return self.entities.get(entity_id)

    def get_entity(self, entity_id: str) -> Optional[GraphEntity]:
        return self.entities.get(entity_id)

    def get_edges(self, subject_id: str, predicate: Optional[str] = None) -> List[GraphEdge]:
        edges = self._out_edges.get(subject_id, [])
        if not predicate:
            return list(edges)
        return [edge for edge in edges if edge.type == predicate]

    def get_neighbors(
        self,
        entity_id: str,
        edge_types: Optional[List[str]] = None,
        depth: int = 1,
    ) -> List[GraphEdge]:
        if depth <= 0:
            return []

        frontier = [entity_id]
        visited = set(frontier)
        collected: List[GraphEdge] = []

        for _ in range(depth):
            next_frontier = []
            for current in frontier:
                for edge in self._out_edges.get(current, []):
                    if edge_types and edge.type not in edge_types:
                        continue
                    collected.append(edge)
                    if edge.target_id not in visited:
                        visited.add(edge.target_id)
                        next_frontier.append(edge.target_id)
            frontier = next_frontier

        return collected


_GRAPH_INSTANCE: Optional[InMemoryGraphStore] = None


def get_world_graph() -> InMemoryGraphStore:
    global _GRAPH_INSTANCE
    if _GRAPH_INSTANCE is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        entities_path = os.path.join(base_dir, "data", "entities.json")
        edges_path = os.path.join(base_dir, "data", "edges.json")
        _GRAPH_INSTANCE = InMemoryGraphStore(entities_path, edges_path)
    return _GRAPH_INSTANCE
