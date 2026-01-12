# Configuration for the World Dialogue System

# ===== LLM Provider Selection =====
# Set to "google" for Google Generative AI, or "lmstudio" for local LM Studio
LLM_PROVIDER = "google"  # Options: "google" | "lmstudio"

# ===== Google Generative AI Configuration =====
Vertex_API_KEY = "key"
GCP_PROJECT_ID = "id"

# ===== LM Studio Configuration =====
# LM Studio runs a local OpenAI-compatible API
LMSTUDIO_HOST = "localhost"
LMSTUDIO_PORT = 1234
LMSTUDIO_MODEL = "default"  # Model name to use (check LM Studio UI for available models)