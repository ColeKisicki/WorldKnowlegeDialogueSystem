"""
Main entry point for the world dialogue system.
Sets up and runs an interactive NPC dialogue session using LangGraph.
"""

import argparse
import logging

from Dialogue.entities.npc import NPC
from Dialogue.dialogue_graph import (
    create_dialogue_graph,
    get_dialogue_graph_mermaid,
    run_dialogue_turn,
)
from Dialogue.live_viewer import start_trace_server
from Dialogue.trace import enable_trace


def create_sample_npc() -> NPC:
    """Create a sample NPC for testing."""
    return NPC(
        entity_id="ent_aldric",
        name="Aldric",
    )


def main():
    """Run an interactive NPC dialogue session."""
    parser = argparse.ArgumentParser(description="World Dialogue System CLI")
    parser.add_argument(
        "--retrieval-debug",
        action="store_true",
        help="Enable detailed retrieval logging",
    )
    parser.add_argument(
        "--show-graph",
        action="store_true",
        help="Print the dialogue graph in Mermaid format",
    )
    parser.add_argument(
        "--live-viewer",
        action="store_true",
        help="Start the live trace viewer",
    )
    parser.add_argument(
        "--live-viewer-port",
        type=int,
        default=8765,
        help="Port for the live trace viewer",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    if args.retrieval_debug:
        logging.getLogger("Dialogue.nodes.graph_retrieval").setLevel(logging.DEBUG)
        logging.getLogger("Dialogue.nodes.vector_retrieval").setLevel(logging.DEBUG)
    if args.show_graph:
        mermaid = get_dialogue_graph_mermaid()
        print("\n[Dialogue Graph - Mermaid]")
        print(mermaid)
        print()
    if args.live_viewer:
        enable_trace()
        start_trace_server(port=args.live_viewer_port)
        print(f"[Live Viewer] http://127.0.0.1:{args.live_viewer_port}")
        print("[Live Viewer] Writing trace to trace/trace.jsonl\n")
    print("=" * 60)
    print("World Dialogue System - NPC Chat Session")
    print("=" * 60)
    print("(Type 'quit' or 'exit' to end the session)")
    print("(Type 'clear' to clear conversation history)")
    print("=" * 60)
    print()
    
    # Create sample NPC
    npc = create_sample_npc()
    print(f"You are speaking with: {npc.name}\n")
    
    # Create the dialogue graph (stateless, reusable)
    graph = create_dialogue_graph()
    
    # Track conversation history
    conversation_history = ""
    
    # Main conversation loop
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["quit", "exit"]:
                print("Goodbye!")
                break
            
            if user_input.lower() == "clear":
                conversation_history = ""
                print("[Conversation history cleared]")
                continue
            
            # Run dialogue turn through the graph
            response = run_dialogue_turn(graph, npc, user_input, conversation_history)
            print(f"\n{npc.name}: {response}\n")
            
            # Update conversation history for next turn
            conversation_history += f"Human: {user_input}\n{npc.name}: {response}\n\n"
        
        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again.\n")


if __name__ == "__main__":
    main()
