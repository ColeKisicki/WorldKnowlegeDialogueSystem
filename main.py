"""
Main entry point for the world dialogue system.
Sets up and runs an interactive NPC dialogue session using LangGraph.
"""

from Dialogue.entities.npc import NPC
from Dialogue.dialogue_graph import create_dialogue_graph, run_dialogue_turn


def create_sample_npc() -> NPC:
    """Create a sample NPC for testing."""
    return NPC(
        name="Aldric",
        age=45,
        location="The Crooked Tavern, Port Valor",
        profession="Tavern Keeper",
        traits=["observant", "gruff", "curious", "skeptical"],
        childhood_backstory="Born to a fisherman's family in Port Valor. Spent youth learning the docks and the people who sailed them. Lost his father to a storm at sea when he was twelve.",
        adult_backstory="Inherited the Crooked Tavern from his uncle at 25. Has run it for twenty years, making it a hub for sailors, merchants, and adventurers. Has heard countless stories and seen the rise and fall of fortunes."
    )


def main():
    """Run an interactive NPC dialogue session."""
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