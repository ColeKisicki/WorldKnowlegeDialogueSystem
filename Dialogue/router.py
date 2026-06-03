import json
from typing import Dict, List, Optional

from Dialogue.llm.provider import LLMProvider
from Dialogue.router_models import QuerySpec, Intent, LocationBias, LocationBiasMode


SYSTEM_PROMPT = (
    "You are a query router for a fictional world assistant. "
    "Output ONLY valid JSON. Do not include markdown or comments. "
    "JSON must match the schema exactly. "
    "If uncertain, choose ASK_ENTITY_FACTS. "
    "Resolve relative time phrases: lately/recently/these days -> 14, "
    "last week -> 7, last month -> 30, today -> 1, yesterday -> 2, "
    "otherwise 0. "
    "Location bias: default NEAR_NPC. "
    "If user mentions a place explicitly, use SPECIFIC_LOCATION + that name. "
    "Extract named entities (orgs, locations, items) into entities. "
    "Do not output relationship phrases as entities (e.g., \"Aldric's sister\"). "
    "Use subject_entity for the main entity being asked about and relationship_term "
    "for the relationship word or phrase (e.g., sister, owner, leader). "
    "If the subject is ambiguous (e.g., she/he/they/it) and RECENT_ENTITIES are "
    "provided, select the most contextually relevant recent entity as subject_entity. "
    "Set needs_retrieval=false for greetings, chit-chat, or messages that do not "
    "require world knowledge."
)

DEV_PROMPT = """Schema:
{
  "intent": "ASK_EVENTS | ASK_ENTITY_FACTS | ASK_LOCATION | ASK_HOW_TO | ASK_RELATIONSHIP | ASK_COMPARISON | ASK_COUNT | SMALLTALK | OTHER",
  "query_text": "string",
  "entities": [{"name": "string", "type": "NPC | ORG | FACTION | LOCATION | ITEM | EVENT | UNKNOWN"}],
  "needs_retrieval": true,
  "subject_entity": "string",
  "relationship_term": "string",
  "time_window_days": 0,
  "time_constraint_text": "string",
  "location_bias": {"mode": "NEAR_NPC | SPECIFIC_LOCATION | NONE", "location_name": "string"},
  "answer_format": "BRIEF | NORMAL | DETAILED"
}

Examples:
Input: Have you heard about any bandit attacks lately?
Output: {"intent":"ASK_EVENTS","query_text":"bandit attacks","entities":[],"needs_retrieval":true,"subject_entity":"","relationship_term":"","time_window_days":14,"time_constraint_text":"lately","location_bias":{"mode":"NEAR_NPC","location_name":""},"answer_format":"NORMAL"}

Input: What happened on the North Road last week?
Output: {"intent":"ASK_EVENTS","query_text":"what happened on the North Road","entities":[{"name":"North Road","type":"LOCATION"}],"needs_retrieval":true,"subject_entity":"North Road","relationship_term":"","time_window_days":7,"time_constraint_text":"last week","location_bias":{"mode":"SPECIFIC_LOCATION","location_name":"North Road"},"answer_format":"NORMAL"}

Input: Where can I find Sunleaf?
Output: {"intent":"ASK_LOCATION","query_text":"find Sunleaf","entities":[{"name":"Sunleaf","type":"ITEM"}],"needs_retrieval":true,"subject_entity":"Sunleaf","relationship_term":"location","time_window_days":0,"time_constraint_text":"","location_bias":{"mode":"NEAR_NPC","location_name":""},"answer_format":"NORMAL"}

Input: What do the Iron Guard do?
Output: {"intent":"ASK_ENTITY_FACTS","query_text":"Iron Guard role","entities":[{"name":"Iron Guard","type":"ORG"}],"needs_retrieval":true,"subject_entity":"Iron Guard","relationship_term":"role","time_window_days":0,"time_constraint_text":"","location_bias":{"mode":"NEAR_NPC","location_name":""},"answer_format":"NORMAL"}

Input: What is the Lantern Guild responsible for?
Output: {"intent":"ASK_ENTITY_FACTS","query_text":"Lantern Guild responsibilities","entities":[{"name":"Lantern Guild","type":"ORG"}],"needs_retrieval":true,"subject_entity":"Lantern Guild","relationship_term":"responsibilities","time_window_days":0,"time_constraint_text":"","location_bias":{"mode":"NEAR_NPC","location_name":""},"answer_format":"NORMAL"}

Input: Who does the Ironwatch report to?
Output: {"intent":"ASK_RELATIONSHIP","query_text":"Ironwatch chain of command","entities":[{"name":"Ironwatch","type":"ORG"}],"needs_retrieval":true,"subject_entity":"Ironwatch","relationship_term":"chain of command","time_window_days":0,"time_constraint_text":"","location_bias":{"mode":"NEAR_NPC","location_name":""},"answer_format":"NORMAL"}

Input: Who leads the Ironwatch?
Output: {"intent":"ASK_RELATIONSHIP","query_text":"Ironwatch leader","entities":[{"name":"Ironwatch","type":"ORG"}],"needs_retrieval":true,"subject_entity":"Ironwatch","relationship_term":"leader","time_window_days":0,"time_constraint_text":"","location_bias":{"mode":"NEAR_NPC","location_name":""},"answer_format":"NORMAL"}

Input: Who is Captain Voss?
Output: {"intent":"ASK_ENTITY_FACTS","query_text":"Captain Voss","entities":[{"name":"Captain Voss","type":"NPC"}],"needs_retrieval":true,"subject_entity":"Captain Voss","relationship_term":"","time_window_days":0,"time_constraint_text":"","location_bias":{"mode":"NEAR_NPC","location_name":""},"answer_format":"NORMAL"}

Input: Is Port Valor bigger than Grayfall?
Output: {"intent":"ASK_COMPARISON","query_text":"Port Valor compared to Grayfall","entities":[{"name":"Port Valor","type":"LOCATION"},{"name":"Grayfall","type":"LOCATION"}],"needs_retrieval":true,"subject_entity":"Port Valor","relationship_term":"comparison","time_window_days":0,"time_constraint_text":"","location_bias":{"mode":"NONE","location_name":""},"answer_format":"NORMAL"}

Input: How many ships disappeared this season?
Output: {"intent":"ASK_COUNT","query_text":"ships disappeared this season","entities":[],"needs_retrieval":true,"subject_entity":"","relationship_term":"count","time_window_days":0,"time_constraint_text":"this season","location_bias":{"mode":"NEAR_NPC","location_name":""},"answer_format":"NORMAL"}

Input: Hi there.
Output: {"intent":"SMALLTALK","query_text":"hi","entities":[],"needs_retrieval":false,"subject_entity":"","relationship_term":"","time_window_days":0,"time_constraint_text":"","location_bias":{"mode":"NEAR_NPC","location_name":""},"answer_format":"NORMAL"}

Input: How old is your sister?
Output: {"intent":"ASK_RELATIONSHIP","query_text":"sister age","entities":[{"name":"Aldric","type":"NPC"}],"needs_retrieval":true,"subject_entity":"Aldric","relationship_term":"sister","time_window_days":0,"time_constraint_text":"","location_bias":{"mode":"NEAR_NPC","location_name":""},"answer_format":"NORMAL"}

Input: Tell me about Prince Theron.
Output: {"intent":"ASK_ENTITY_FACTS","query_text":"Prince Theron","entities":[{"name":"Prince Theron","type":"NPC"}],"time_window_days":0,"time_constraint_text":"","location_bias":{"mode":"NEAR_NPC","location_name":""},"answer_format":"NORMAL"}
"""


def _build_user_block(
    user_text: str,
    npc_context: Dict[str, str],
    world_hints: Optional[Dict[str, List[str]]],
    recent_entities: Optional[List[str]] = None,
) -> str:
    lines = [
        f"NPC_ID: {npc_context.get('npc_id', '')}",
        f"NPC_NAME: {npc_context.get('npc_name', '')}",
        f"NPC_LOCATION: {npc_context.get('npc_location', '')}",
        f"WORLD_DATE: {npc_context.get('world_date', '')}",
        f"USER_MESSAGE: {user_text}",
    ]

    if world_hints:
        orgs = "; ".join(world_hints.get("org_names", []))
        locations = "; ".join(world_hints.get("location_names", []))
        npcs = "; ".join(world_hints.get("npc_names", []))
        items = "; ".join(world_hints.get("item_names", []))
        if orgs:
            lines.append(f"KNOWN_ORGS: {orgs}")
        if locations:
            lines.append(f"KNOWN_LOCATIONS: {locations}")
        if npcs:
            lines.append(f"KNOWN_NPCS: {npcs}")
        if items:
            lines.append(f"KNOWN_ITEMS: {items}")

    if recent_entities:
        lines.append(f"RECENT_ENTITIES: {'; '.join(recent_entities)}")

    return "\n".join(lines)


def _extract_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`").strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return ""
    return text[start : end + 1]


def _fallback_spec(user_text: str) -> QuerySpec:
    return QuerySpec(
        intent=Intent.ASK_ENTITY_FACTS,
        query_text=user_text,
        entities=[],
        time_window_days=0,
        time_constraint_text="",
        location_bias=LocationBias(mode=LocationBiasMode.NEAR_NPC, location_name=""),
        answer_format="NORMAL",
    )


def route_query(
    user_text: str,
    npc_context: Dict[str, str],
    world_hints: Optional[Dict[str, List[str]]] = None,
    recent_entities: Optional[List[str]] = None,
) -> QuerySpec:
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"{DEV_PROMPT}\n\n"
        f"{_build_user_block(user_text, npc_context, world_hints, recent_entities)}"
    )

    raw = LLMProvider.generate(prompt)
    json_blob = _extract_json(raw)
    if json_blob:
        try:
            return QuerySpec.model_validate_json(json_blob)
        except Exception:
            pass

    retry_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        "Your previous output was invalid JSON. Output ONLY valid JSON.\n\n"
        f"{_build_user_block(user_text, npc_context, world_hints, recent_entities)}"
    )
    raw_retry = LLMProvider.generate(retry_prompt)
    json_blob = _extract_json(raw_retry)
    if json_blob:
        try:
            return QuerySpec.model_validate_json(json_blob)
        except Exception:
            pass

    return _fallback_spec(user_text)
