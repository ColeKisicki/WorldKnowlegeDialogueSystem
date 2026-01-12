"""
Utility for building the Chroma index from the JSON world data.
"""

from World.store import get_world_store


def build_world_index(reset: bool = False) -> None:
    store = get_world_store(reset_index=reset)
    store.build_index(reset=reset)


if __name__ == "__main__":
    build_world_index(reset=True)
    print("World index built.")
