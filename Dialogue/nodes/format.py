"""
Response formatting nodes for the dialogue graph.
Post-processes LLM responses for presentation.
"""

from Dialogue.state import DialogueState


def format_response(state: DialogueState) -> DialogueState:
    """
    Node: Format the raw response for presentation.
    
    This node performs post-processing on the LLM response:
    - Strips whitespace
    - Cleans up formatting
    - Could add emoji, markdown, etc.
    
    Future extensibility: This is where audit trail formatting would happen
    (e.g., adding citations for facts used).
    
    Args:
        state: Current dialogue state with raw_response populated
        
    Returns:
        Updated state with formatted_response populated
    """
    raw_response = state.get("raw_response", "")
    formatted = raw_response.strip()
    
    state["formatted_response"] = formatted
    return state
