import json
import os
import threading
import time
from typing import Any, Dict, List, Tuple


_TRACE_ENABLED = False
_TRACE_EVENTS: List[Dict[str, Any]] = []
_TRACE_LOCK = threading.Lock()
_TRACE_OUTPUT_PATH = ""
_TRACE_NEXT_ID = 1


def enable_trace(output_dir: str = "trace") -> None:
    global _TRACE_ENABLED, _TRACE_OUTPUT_PATH, _TRACE_NEXT_ID
    os.makedirs(output_dir, exist_ok=True)
    _TRACE_OUTPUT_PATH = os.path.join(output_dir, "trace.jsonl")
    with open(_TRACE_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("")
    _TRACE_NEXT_ID = 1
    _TRACE_ENABLED = True


def trace_enabled() -> bool:
    return _TRACE_ENABLED


def _serialize_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _serialize_value(val) for key, val in value.items()}

    npc_fields = ["name", "age", "location", "profession", "traits"]
    if all(hasattr(value, field) for field in npc_fields):
        return {field: getattr(value, field) for field in npc_fields}

    if hasattr(value, "__dict__"):
        return {key: _serialize_value(val) for key, val in value.__dict__.items()}

    return str(value)


def _serialize_state(state: Dict[str, Any]) -> Dict[str, Any]:
    return {key: _serialize_value(val) for key, val in state.items()}


def record_trace(node_name: str, state: Dict[str, Any]) -> None:
    if not _TRACE_ENABLED:
        return
    global _TRACE_NEXT_ID
    event = {
        "id": _TRACE_NEXT_ID,
        "timestamp": time.time(),
        "node": node_name,
        "state": _serialize_state(state),
    }
    _TRACE_NEXT_ID += 1
    with _TRACE_LOCK:
        _TRACE_EVENTS.append(event)
        if _TRACE_OUTPUT_PATH:
            with open(_TRACE_OUTPUT_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(event))
                f.write("\n")


def get_events_since(event_id: int) -> Tuple[List[Dict[str, Any]], int]:
    with _TRACE_LOCK:
        if not _TRACE_EVENTS:
            return [], event_id
        events = [event for event in _TRACE_EVENTS if event["id"] > event_id]
        next_id = _TRACE_EVENTS[-1]["id"] if _TRACE_EVENTS else event_id
        return events, next_id
