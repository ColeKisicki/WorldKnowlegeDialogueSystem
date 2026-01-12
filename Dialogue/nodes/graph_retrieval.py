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
    npc_context = {
        "npc_id": getattr(npc, "name", "unknown").lower().replace(" ", "_"),
        "npc_name": getattr(npc, "name", ""),
        "npc_location": getattr(npc, "location", ""),
        "world_date": "",
    }

    store = get_world_store()
    world_hints = store.world_hints()
    query_spec = route_query(user_input, npc_context, world_hints)
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

    graph = get_world_graph()
    if graph_spec.graph_intent == graph_spec.graph_intent.NONE:
        state["graph_facts"] = []
        state["graph_neighbor_ids"] = []
        return state
    edge_types = graph_spec.edge_types or None

    entity_names = [entity.name for entity in query_spec.entities]
    if not entity_names and npc is not None:
        entity_names = [getattr(npc, "name", "")]
    entity_ids = store.resolve_entity_ids(entity_names)
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

    state["graph_facts"] = graph_facts
    state["graph_neighbor_ids"] = list(neighbor_entity_ids)
    if graph_facts:
        LOGGER.info("Graph facts=%d", len(graph_facts))
        LOGGER.debug("Graph facts detail:")
        for fact in graph_facts:
            LOGGER.debug("  - %s", fact)

    record_trace("retrieve_graph_knowledge", state)
    return state
