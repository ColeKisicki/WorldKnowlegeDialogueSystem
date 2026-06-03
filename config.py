# Configuration for the World Dialogue System

# ===== LLM Provider Selection =====
# Set to "google" for Google Generative AI, or "lmstudio" for local LM Studio
LLM_PROVIDER = "google"  # Options: "google" | "lmstudio"

# ===== Google Generative AI Configuration =====
Vertex_API_KEY = "AIzaSyAFbik1Hcne6BtRU24zEbryYZLycguE5fc"
GCP_PROJECT_ID = "worlddialoguesystem"

# ===== LM Studio Configuration =====
# LM Studio runs a local OpenAI-compatible API
LMSTUDIO_HOST = "localhost"
LMSTUDIO_PORT = 1234
LMSTUDIO_MODEL = "default"  # Model name to use (check LM Studio UI for available models)

# ===== Graph Backend Configuration =====
# Options: "memory" | "neo4j"
GRAPH_BACKEND = "memory"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4jpassword"
