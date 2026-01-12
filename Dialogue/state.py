"""
State definitions for the dialogue graph.
Defines the structure of data flowing through the dialogue system.
"""

from typing import TypedDict, List, Dict, Any
from Dialogue.entities.npc import NPC


class DialogueContext(TypedDict):
    """Context about the current dialogue."""
    npc: NPC
    user_input: str
    conversation_history: str


class PromptData(TypedDict):
    """Prompt-related data during dialogue."""
    system_prompt: str
    full_prompt: str


class DialogueResponse(TypedDict):
    """Response data from the LLM."""
    raw_response: str
    formatted_response: str
    # Extensible for future fields: fact_ids, audit_trail, etc.


class DialogueState(TypedDict):
    """
    Complete state for dialogue graph processing.
    
    Separates concerns into:
    - context: Information about NPC and conversation
    - prompts: Prompt construction data
    - response: LLM response data
    """
    # Context (set at start)
    npc: NPC
    user_input: str
    conversation_history: str
    
    # Prompts (built during processing)
    system_prompt: str
    full_prompt: str
    
    # Response (generated and formatted)
    raw_response: str
    formatted_response: str

    # Retrieval (Phase 1 RAG)
    retrieval_results: List[Dict[str, str]]
    query_spec: Dict[str, Any]
    graph_facts: List[str]
    graph_query_spec: Dict[str, Any]
    graph_neighbor_ids: List[str]
    
    # Extensible fields for future phases
    # retrieval_results: Optional[List[str]]  # For knowledge retrieval
    # audit_trail: Optional[List[Dict]]        # For fact citations
    # facts_used: Optional[List[str]]          # For tracking source facts
