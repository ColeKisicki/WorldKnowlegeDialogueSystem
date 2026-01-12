"""
LLM nodes for the dialogue graph.
Handles calling the language model.
"""

from Dialogue.state import DialogueState
from Dialogue.llm.provider import LLMProvider


def call_llm(state: DialogueState) -> DialogueState:
    """
    Node: Call the LLM with the full prompt.
    
    This node invokes the language model to generate a response based on the
    constructed prompt. The LLM provider handles all API interactions and
    supports multiple backends (Google, LM Studio, etc).
    
    Args:
        state: Current dialogue state with full_prompt populated
        
    Returns:
        Updated state with raw_response populated
        
    Raises:
        Exception: If the LLM call fails
    """
    try:
        full_prompt = state.get("full_prompt", "")
        if not full_prompt:
            raise ValueError("full_prompt is required but empty")
        
        # Use the factory to get the configured provider
        response = LLMProvider.generate(full_prompt)
        state["raw_response"] = response
        
    except Exception as e:
        # Store error in response for graceful handling
        state["raw_response"] = f"[Error generating response: {str(e)}]"
    
    return state
