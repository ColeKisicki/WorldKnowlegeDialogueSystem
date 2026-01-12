"""
Vector retrieval node for world knowledge.
Fetches semantic and entity-linked facts from the vector store.
"""

import logging

from Dialogue.state import DialogueState
from Dialogue.trace import record_trace
from World.store import get_world_store
from World.visualize import print_retrieval_results


LOGGER = logging.getLogger(__name__)


def _log_hits(label: str, hits: list[dict]) -> None:
    if not hits:
        LOGGER.debug("%s hits: none", label)
        return
    LOGGER.debug("%s hits:", label)
    for hit in hits:
        hit_id = hit.get("id", "unknown")
        text = hit.get("text", "").strip()
        entity = hit.get("entity_name", "unknown")
        score = hit.get("score", "n/a")
        LOGGER.debug("  - %s | %s | score=%s | %s", hit_id, entity, score, text)


def retrieve_vector_knowledge(state: DialogueState) -> DialogueState:
    user_input = state.get("user_input", "")
    query_spec = state.get("query_spec", {})
    if not query_spec.get("needs_retrieval", True):
        LOGGER.info("Vector retrieval skipped (needs_retrieval=false)")
        state["retrieval_results"] = []
        return state

    query_text = query_spec.get("query_text") or user_input

    store = get_world_store()
    semantic_hits = store.search(query_text, n_results=5)
    LOGGER.info("Vector semantic hits=%d", len(semantic_hits))
    _log_hits("Vector semantic", semantic_hits)

    entity_hits = []
    entity_names = [entity.get("name") for entity in query_spec.get("entities", [])]
    for entity_id in store.resolve_entity_ids(entity_names):
        entity_hits.extend(store.facts_for_entity(entity_id, limit=3))

    if entity_hits:
        LOGGER.info("Vector entity-linked hits=%d", len(entity_hits))
        _log_hits("Vector entity-linked", entity_hits)

    related_hits = []
    for neighbor_id in state.get("graph_neighbor_ids", []):
        related_hits.extend(store.facts_for_entity(neighbor_id, limit=2))
    if related_hits:
        LOGGER.info("Vector neighbor hits=%d", len(related_hits))
        _log_hits("Vector neighbor", related_hits)

    combined = semantic_hits + entity_hits + related_hits
    if combined:
        seen = set()
        deduped = []
        for hit in combined:
            hit_id = hit.get("id")
            if not hit_id or hit_id in seen:
                continue
            seen.add(hit_id)
            deduped.append(hit)
        combined = deduped

    state["retrieval_results"] = combined

    if LOGGER.isEnabledFor(logging.DEBUG):
        print_retrieval_results(combined)

    record_trace("retrieve_vector_knowledge", state)
    return state
