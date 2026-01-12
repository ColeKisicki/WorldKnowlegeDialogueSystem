"""
Prompt building nodes for the dialogue graph.
Constructs the full prompt from various sources.
"""

from Dialogue.state import DialogueState


def build_prompt(state: DialogueState) -> DialogueState:
    """
    Node: Build the full prompt from system prompt, history, and user input.
    
    This node combines:
    - System prompt (NPC character context)
    - Conversation history (previous exchanges)
    - User input (current message)
    
    Future extensibility: This is where knowledge retrieval results would be injected.
    
    Args:
        state: Current dialogue state
        
    Returns:
        Updated state with full_prompt populated
    """
    system_prompt = state.get("system_prompt", "")
    history = state.get("conversation_history", "")
    user_input = state.get("user_input", "")
    
    # Build full prompt
    full_prompt = f"""{system_prompt}"""
    
    if history:
        full_prompt += f"\n\n{history}"
    
    full_prompt += f"\nHuman: {user_input}\nAI:"
    
    state["full_prompt"] = full_prompt
    return state
