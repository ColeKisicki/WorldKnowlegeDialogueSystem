"""
Main dialogue graph orchestration.
Composes individual nodes into a complete dialogue processing pipeline.
"""

from langgraph.graph import StateGraph, START, END
from Dialogue.state import DialogueState
from Dialogue.nodes.context import load_npc_context
from Dialogue.nodes.prompt import build_prompt
from Dialogue.nodes.llm import call_llm
from Dialogue.nodes.format import format_response
from Dialogue.entities.npc import NPC


def create_dialogue_graph():
    """
    Create and compile the dialogue state graph.
    
    Graph structure:
        START
          ↓
        load_npc_context     (Format NPC into system prompt)
          ↓
        build_prompt         (Construct full prompt)
          ↓
        call_llm             (Call LLM API)
          ↓
        format_response      (Post-process response)
          ↓
        END
    
    Future extensibility notes:
    - Add a "retrieve_knowledge" node between build_prompt and call_llm
      to inject world facts into the prompt
    - Add conditional routing for error handling
    - Add audit trail tracking node before format_response
    
    Returns:
        A compiled LangGraph that processes dialogue turns.
    """
    graph = StateGraph(DialogueState)
    
    # Add nodes in logical order
    graph.add_node("load_npc", load_npc_context)
    graph.add_node("build_prompt", build_prompt)
    graph.add_node("call_llm", call_llm)
    graph.add_node("format_response", format_response)
    
    # Define edges (linear for now, can add conditionals later)
    graph.add_edge(START, "load_npc")
    graph.add_edge("load_npc", "build_prompt")
    graph.add_edge("build_prompt", "call_llm")
    graph.add_edge("call_llm", "format_response")
    graph.add_edge("format_response", END)
    
    # Compile the graph
    return graph.compile()


def run_dialogue_turn(graph, npc: NPC, user_input: str, conversation_history: str = "") -> str:
    """
    Run a single dialogue turn through the graph.
    
    Args:
        graph: The compiled dialogue graph
        npc: The NPC character
        user_input: User's message
        conversation_history: Previous conversation (for context)
        
    Returns:
        The NPC's formatted response
    """
    initial_state: DialogueState = {
        "npc": npc,
        "user_input": user_input,
        "conversation_history": conversation_history,
        "system_prompt": "",
        "full_prompt": "",
        "raw_response": "",
        "formatted_response": "",
    }
    
    result = graph.invoke(initial_state)
    return result["formatted_response"]

