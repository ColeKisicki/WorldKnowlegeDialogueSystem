"""
Graph retrieval node for world knowledge.
Fetches graph facts and neighbor entity ids for later vector expansion.
"""

import logging

from Dialogue.graph_router import route_graph_query
from Dialogue.router import route_query
from Dialogue.state import DialogueState
from Dialogue.trace import record_trace
from World.graph_store import get_world_graph
from World.store import get_world_store


LOGGER = logging.getLogger(__name__)

AVAILABLE_EDGE_TYPES = [
    "KINSHIP",
    "INHERITED_FROM",
    "OWNS",
    "OWNED",
    "LOCATED_IN",
    "OPERATES_IN",
    "CONNECTS",
    "INVOLVED_IN",
    "HAPPENED_AT",
    "CAUSES",
]


def retrieve_graph_knowledge(state: DialogueState) -> DialogueState:
    user_input = state.get("user_input", "")
    npc = state.get("npc")
    graph = get_world_graph()
    npc_entity = None
    if npc:
        npc_entity = graph.get_entity(getattr(npc, "entity_id", "")) or graph.get_entity_by_name(
            getattr(npc, "name", "")
        )
    npc_context = {
        "npc_id": getattr(npc, "entity_id", getattr(npc, "name", "unknown")).lower().replace(" ", "_")
        if npc
        else "unknown",
        "npc_name": getattr(npc, "name", "") if npc else "",
        "npc_location": "",
        "world_date": "",
    }
    if npc_entity and npc_entity.properties.get("location"):
        npc_context["npc_location"] = str(npc_entity.properties.get("location"))

    store = get_world_store()
    world_hints = store.world_hints()
    recent_entities = state.get("recent_entities", [])
    query_spec = route_query(user_input, npc_context, world_hints, recent_entities)
    state["query_spec"] = query_spec.model_dump()
    LOGGER.info("Router intent=%s query='%s'", query_spec.intent, query_spec.query_text)

    graph_spec = route_graph_query(
        user_input,
        [entity.model_dump() for entity in query_spec.entities],
        AVAILABLE_EDGE_TYPES,
    )
    state["graph_query_spec"] = graph_spec.model_dump()
    LOGGER.info(
        "Graph router intent=%s edges=%s",
        graph_spec.graph_intent,
        ",".join(graph_spec.edge_types),
    )

    if graph_spec.graph_intent == graph_spec.graph_intent.NONE:
        state["graph_facts"] = []
        state["graph_neighbor_ids"] = []
        return state
    edge_types = graph_spec.edge_types or None

    entity_names = [entity.name for entity in query_spec.entities]
    subject_entity = query_spec.subject_entity or ""
    if subject_entity:
        filtered_entity_names = [subject_entity]
    elif not entity_names and npc is not None:
        filtered_entity_names = [getattr(npc, "name", "")]
    else:
        filtered_entity_names = entity_names
    entity_ids = store.resolve_entity_ids(filtered_entity_names)
    if not entity_ids and npc is not None:
        entity_ids = store.resolve_entity_ids([getattr(npc, "name", "")])
    neighbor_entity_ids = set()
    graph_facts = []

    for entity_id in entity_ids:
        edges = graph.get_neighbors(entity_id, edge_types=edge_types, depth=1)
        for edge in edges:
            source = graph.get_entity(edge.source_id)
            target = graph.get_entity(edge.target_id)
            source_name = source.name if source else edge.source_id
            target_name = target.name if target else edge.target_id
            relation = edge.type.lower().replace("_", " ")
            props = edge.properties
            if props:
                prop_text = ", ".join(f"{key}={value}" for key, value in props.items())
                graph_facts.append(
                    f"{source_name} {relation} {target_name} ({prop_text})"
                )
            else:
                graph_facts.append(f"{source_name} {relation} {target_name}")
            neighbor_entity_ids.add(edge.target_id)

    for neighbor_id in neighbor_entity_ids:
        neighbor = graph.get_entity(neighbor_id)
        if not neighbor:
            continue
        props = neighbor.properties or {}
        for key, value in props.items():
            if value in (None, "", [], {}):
                continue
            if isinstance(value, list):
                value_text = ", ".join(str(item) for item in value)
            else:
                value_text = str(value)
            graph_facts.append(f"{neighbor.name} {key} {value_text}")

    state["graph_facts"] = graph_facts
    state["graph_neighbor_ids"] = list(neighbor_entity_ids)
    if graph_facts:
        LOGGER.info("Graph facts=%d", len(graph_facts))
        LOGGER.debug("Graph facts detail:")
        for fact in graph_facts:
            LOGGER.debug("  - %s", fact)

    record_trace("retrieve_graph_knowledge", state)
    return state
