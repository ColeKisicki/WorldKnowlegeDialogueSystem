import json
import os
from typing import Dict, List

from neo4j import GraphDatabase


def load_json(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_entities(session, entities: List[Dict]) -> None:
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE")
    session.run(
        """
        UNWIND $entities AS e
        MERGE (n:Entity {id: e.id})
        SET n += e.props
        """,
        entities=entities,
    )


def load_edges(session, edges: List[Dict]) -> None:
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:REL]-() REQUIRE r.id IS UNIQUE")
    session.run(
        """
        UNWIND $edges AS r
        MATCH (a:Entity {id: r.source_id})
        MATCH (b:Entity {id: r.target_id})
        MERGE (a)-[rel:REL {id: r.id}]->(b)
        SET rel.type = r.type,
            rel.properties_json = r.properties_json
        """,
        edges=edges,
    )


def main() -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    entities_path = os.path.join(base_dir, "..", "World", "data", "entities.json")
    edges_path = os.path.join(base_dir, "..", "World", "data", "edges.json")

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "neo4jpassword")

    entities = load_json(entities_path).get("entities", [])
    for entity in entities:
        props = {key: value for key, value in entity.items() if key != "id"}
        entity["props"] = props
    edges = load_json(edges_path).get("edges", [])
    for edge in edges:
        edge["properties_json"] = json.dumps(edge.get("properties", {}))

    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        load_entities(session, entities)
        load_edges(session, edges)
    driver.close()

    print(f"Imported {len(entities)} entities and {len(edges)} edges into Neo4j.")


if __name__ == "__main__":
    main()
