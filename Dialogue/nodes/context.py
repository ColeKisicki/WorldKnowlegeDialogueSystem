"""
Context preparation nodes for the dialogue graph.
Handles loading and formatting NPC context.
"""

from Dialogue.state import DialogueState
from Dialogue.prompts.system_prompt import get_npc_system_prompt
from Dialogue.trace import record_trace


def load_npc_context(state: DialogueState) -> DialogueState:
    """
    Node: Load and format NPC context into a system prompt.
    
    This node extracts the NPC from the state and generates a system prompt
    that will guide the LLM to roleplay as this character.
    
    Args:
        state: Current dialogue state
        
    Returns:
        Updated state with system_prompt populated
    """
    npc = state.get("npc")
    if npc:
        npc_profile = npc.to_prompt_text()
        state["system_prompt"] = get_npc_system_prompt(npc_profile)
    else:
        state["system_prompt"] = ""
    
    record_trace("load_npc_context", state)
    return state
