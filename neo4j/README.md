# Neo4j Setup (Docker)

This folder provides a local Neo4j instance for the world graph.

## Start (with auto-import)

```bash
cd neo4j
docker compose up -d
```

This will also run a one-shot `neo4j_import` container that loads
`World/data/entities.json` and `World/data/edges.json` into Neo4j.

## Connect

- Browser UI: http://localhost:7474
- Bolt: bolt://localhost:7687
- User: `neo4j`
- Password: `neo4jpassword`

## Stop

```bash
docker compose down
```

## Import world data (manual)

```bash
python neo4j/import_world.py
```

You can override connection settings:

```bash
set NEO4J_URI=bolt://localhost:7687
set NEO4J_USER=neo4j
set NEO4J_PASSWORD=neo4jpassword
python neo4j/import_world.py
```

## Notes

- Data persists in Docker volumes: `neo4j_data`, `neo4j_logs`.
- You can change the password in `docker-compose.yml` (NEO4J_AUTH).
- Re-running `docker compose up -d` will re-run the import container.
