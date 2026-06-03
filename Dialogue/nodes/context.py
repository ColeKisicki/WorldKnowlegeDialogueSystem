"""
Context preparation nodes for the dialogue graph.
Handles loading and formatting NPC context.
"""

from Dialogue.state import DialogueState
from Dialogue.prompts.system_prompt import get_npc_system_prompt
from World.graph_store import get_world_graph
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
    if not npc:
        state["system_prompt"] = ""
        record_trace("load_npc_context", state)
        return state

    graph = get_world_graph()
    entity = graph.get_entity(getattr(npc, "entity_id", "")) or graph.get_entity_by_name(
        getattr(npc, "name", "")
    )

    name = getattr(npc, "name", "")
    if entity and entity.name:
        name = entity.name

    profile_lines = [f"Character Profile: {name}"]
    npc_node_facts = []
    properties = entity.properties if entity else {}
    age = properties.get("age", "")
    location = properties.get("location", "")
    profession = properties.get("profession", "")
    traits = properties.get("traits", [])
    childhood = properties.get("childhood_backstory", "")
    adult = properties.get("adult_backstory", "")

    if age:
        profile_lines.append(f"\nAge: {age}")
        npc_node_facts.append(f"{name} age {age}")
    if location:
        profile_lines.append(f"Location: {location}")
        npc_node_facts.append(f"{name} location {location}")
    if profession:
        profile_lines.append(f"Profession: {profession}")
        npc_node_facts.append(f"{name} profession {profession}")
    if traits:
        traits_text = ", ".join(traits) if isinstance(traits, list) else str(traits)
        profile_lines.append(f"Traits: {traits_text}")
        npc_node_facts.append(f"{name} traits {traits_text}")
    if entity and entity.description:
        npc_node_facts.append(f"{name} description {entity.description}")
    if childhood:
        profile_lines.append(f"\nChildhood Backstory:\n{childhood}")
    if adult:
        profile_lines.append(f"\nAdult Backstory:\n{adult}")

    npc_profile = "\n".join(profile_lines)
    state["system_prompt"] = get_npc_system_prompt(npc_profile)
    state["npc_node_facts"] = npc_node_facts
    
    record_trace("load_npc_context", state)
    return state
