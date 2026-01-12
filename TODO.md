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
