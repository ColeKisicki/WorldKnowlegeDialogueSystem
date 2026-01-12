"""
Retrieval node for world knowledge (Phase 1 RAG).
"""

import logging
import os

from Dialogue.state import DialogueState
from Dialogue.router import route_query
from World.store import get_world_store
from World.visualize import print_retrieval_results


LOGGER = logging.getLogger(__name__)


def retrieve_knowledge(state: DialogueState) -> DialogueState:
    """
    Node: Retrieve relevant world facts for the user's input.

    Uses semantic search + simple alias matching to pull facts
    from the vector store.
    """
    user_input = state.get("user_input", "")
    store = get_world_store()

    npc = state.get("npc")
    npc_context = {
        "npc_id": getattr(npc, "name", "unknown").lower().replace(" ", "_"),
        "npc_name": getattr(npc, "name", ""),
        "npc_location": getattr(npc, "location", ""),
        "world_date": "",
    }
    world_hints = store.world_hints()
    query_spec = route_query(user_input, npc_context, world_hints)

    query_text = query_spec.query_text or user_input
    semantic_hits = store.search(query_text, n_results=5)
    entity_hits = []
    entity_names = [entity.name for entity in query_spec.entities]
    for entity_id in store.resolve_entity_ids(entity_names):
        entity_hits.extend(store.facts_for_entity(entity_id, limit=3))

    # De-duplicate by fact id while preserving order
    seen = set()
    combined = []
    for hit in semantic_hits + entity_hits:
        fact_id = hit.get("id")
        if not fact_id or fact_id in seen:
            continue
        seen.add(fact_id)
        combined.append(hit)

    state["retrieval_results"] = combined
    state["query_spec"] = query_spec.model_dump()

    if os.getenv("WORLD_DEBUG") == "1":
        logging.basicConfig(level=logging.INFO)
        LOGGER.info("User input: %s", user_input)
        LOGGER.info("Query spec: %s", query_spec.model_dump())
        print_retrieval_results(combined)

    return state
