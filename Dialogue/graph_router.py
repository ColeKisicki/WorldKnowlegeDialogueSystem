import json
from typing import Dict, List

from Dialogue.graph_router_models import GraphQuerySpec, GraphIntent
from Dialogue.llm.provider import LLMProvider


GRAPH_SYSTEM_PROMPT = (
    "You are a graph routing assistant. "
    "Output ONLY valid JSON. Do not include markdown or comments. "
    "Choose graph_intent and edge_types for traversing a world graph. "
    "If no graph traversal is needed, use graph_intent NONE and empty edge_types."
)

GRAPH_DEV_PROMPT = """Schema:
{
  "graph_intent": "NONE | RELATIONSHIP | LOCATION | OWNERSHIP | MEMBERSHIP | CAUSALITY | ALL",
  "edge_types": ["KINSHIP", "INHERITED_FROM", "OWNS", "OWNED", "LOCATED_IN", "OPERATES_IN", "CONNECTS", "INVOLVED_IN", "HAPPENED_AT", "CAUSES"],
  "reason": "string"
}

Examples:
Input: Who is Aldric's uncle?
Output: {"graph_intent":"RELATIONSHIP","edge_types":["KINSHIP"],"reason":"Kinship term mentioned."}

Input: Where is the Crooked Tavern?
Output: {"graph_intent":"LOCATION","edge_types":["LOCATED_IN"],"reason":"Location question."}

Input: Who owns the Crooked Tavern?
Output: {"graph_intent":"OWNERSHIP","edge_types":["OWNS","OWNED"],"reason":"Ownership question."}

Input: Tell me about Aldric.
Output: {"graph_intent":"NONE","edge_types":[],"reason":"General facts can be handled by narrative retrieval."}
"""


def _build_user_block(
    user_text: str,
    entities: List[Dict[str, str]],
    available_edge_types: List[str],
) -> str:
    entity_lines = []
    for entity in entities:
        name = entity.get("name", "")
        etype = entity.get("type", "")
        if name:
            entity_lines.append(f"- {name} ({etype})")

    entity_block = "\n".join(entity_lines) if entity_lines else "None"
    edge_block = "; ".join(available_edge_types)

    return "\n".join(
        [
            f"USER_MESSAGE: {user_text}",
            f"ENTITIES: {entity_block}",
            f"AVAILABLE_EDGE_TYPES: {edge_block}",
        ]
    )


def _extract_json(text: str) -> str:
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return ""
    return text[start : end + 1]


def _fallback_spec() -> GraphQuerySpec:
    return GraphQuerySpec(graph_intent=GraphIntent.NONE, edge_types=[], reason="")


def route_graph_query(
    user_text: str,
    entities: List[Dict[str, str]],
    available_edge_types: List[str],
) -> GraphQuerySpec:
    prompt = (
        f"{GRAPH_SYSTEM_PROMPT}\n\n"
        f"{GRAPH_DEV_PROMPT}\n\n"
        f"{_build_user_block(user_text, entities, available_edge_types)}"
    )

    raw = LLMProvider.generate(prompt)
    json_blob = _extract_json(raw)
    if json_blob:
        try:
            return GraphQuerySpec.model_validate_json(json_blob)
        except Exception:
            pass

    retry_prompt = (
        f"{GRAPH_SYSTEM_PROMPT}\n\n"
        "Your previous output was invalid JSON. Output ONLY valid JSON.\n\n"
        f"{_build_user_block(user_text, entities, available_edge_types)}"
    )
    raw_retry = LLMProvider.generate(retry_prompt)
    json_blob = _extract_json(raw_retry)
    if json_blob:
        try:
            return GraphQuerySpec.model_validate_json(json_blob)
        except Exception:
            pass

    return _fallback_spec()
