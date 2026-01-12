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
    retrieval_results = state.get("retrieval_results", [])
    
    # Build full prompt
    full_prompt = f"""{system_prompt}"""

    facts_lines = []
    for fact in retrieval_results:
        fact_id = fact.get("id", "unknown")
        text = fact.get("text", "")
        if text:
            facts_lines.append(f"- ({fact_id}) {text}")

    if facts_lines:
        facts_block = "\n".join(facts_lines)
    else:
        facts_block = "None."

    full_prompt += f"\n\nWORLD FACTS:\n{facts_block}"
    
    if history:
        full_prompt += f"\n\n{history}"
    
    full_prompt += f"\nHuman: {user_input}\nAI:"
    
    state["full_prompt"] = full_prompt
    return state
