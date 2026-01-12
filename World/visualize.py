import logging
from typing import Dict, List


LOGGER = logging.getLogger(__name__)


def format_retrieval_results(results: List[Dict[str, str]]) -> str:
    if not results:
        return "No facts retrieved."

    lines = ["Retrieved facts:"]
    for idx, fact in enumerate(results, start=1):
        fact_id = fact.get("id", "unknown")
        text = fact.get("text", "").strip()
        entity = fact.get("entity_name", "unknown")
        score = fact.get("score", "n/a")
        lines.append(f"{idx}. {fact_id} | {entity} | score={score} | {text}")
    return "\n".join(lines)


def print_retrieval_results(results: List[Dict[str, str]]) -> None:
    LOGGER.info(format_retrieval_results(results))


def print_world_summary(entities: Dict[str, object], facts: Dict[str, object]) -> None:
    LOGGER.info("World summary: %d entities, %d facts", len(entities), len(facts))
