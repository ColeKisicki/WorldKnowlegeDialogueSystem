TODOs for Retrieval Quality

1) Problem: Generic queries like "hi" still trigger vector retrieval and return
   arbitrary top-k facts because the embedding similarity will always return
   nearest neighbors, even for non-informative queries.

   Location in chain:
   - Dialogue/nodes/vector_retrieval.py -> retrieve_vector_knowledge()
   - Query is derived from QuerySpec.query_text ("hi") and passed to
     World/store.py -> search() with n_results=5.

   Impact:
   - WORLD FACTS block in Dialogue/nodes/prompt.py is populated with unrelated
     facts for smalltalk or low-information queries.

   Desired improvement:
   - Add a retrieval gating strategy (e.g., query-quality check, score threshold,
     or relative-distance filtering) before or after vector search.
   - Consider a lightweight heuristic or learned filter that avoids injecting
     low-confidence results into the prompt.

2) Problem: Router currently receives full KNOWN_* lists from world hints, which
   does not scale when the entity set grows large.

   Location in chain:
   - Dialogue/nodes/graph_retrieval.py -> route_query(..., world_hints)
   - Dialogue/router.py prompt includes KNOWN_ORGS / KNOWN_LOCATIONS / KNOWN_NPCS

   Impact:
   - Prompt size grows with world size.
   - Router inference cost and error rate increase with large lists.

   Desired improvement:
   - Add candidate entity generation before router: small shortlist from alias
     match and/or vector search over entity names.
   - Pass only candidate entities (plus recent entities) into the router.
