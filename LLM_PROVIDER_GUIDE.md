# LLM Provider Configuration Guide

## Quick Switch

To switch between LLM providers, edit `config.py` and change the `LLM_PROVIDER` variable:

```python
# In config.py

# Use Google Generative AI
LLM_PROVIDER = "google"

# OR use local LM Studio
LLM_PROVIDER = "lmstudio"
```

---

## Google Generative AI (Default)

**Setup:**
1. Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add it to `config.py`:
   ```python
   LLM_PROVIDER = "google"
   Vertex_API_KEY = "your-api-key-here"
   ```

**Pros:**
- Cloud-hosted, no local setup
- Fast responses
- Supports latest models (Gemini 2.0 Flash, etc.)

**Cons:**
- Requires API key and internet connection
- Rate limited on free tier
- Data sent to Google servers

---

## LM Studio (Local)

**Setup:**
1. Download and install [LM Studio](https://lmstudio.ai/)
2. Load a model in LM Studio
3. Start the local server (it will listen on port 1234 by default)
4. Update `config.py`:
   ```python
   LLM_PROVIDER = "lmstudio"
   LMSTUDIO_HOST = "localhost"
   LMSTUDIO_PORT = 1234
   LMSTUDIO_MODEL = "default"  # Check LM Studio UI for model name
   ```

**Pros:**
- Runs locally, no internet needed
- Full privacy
- No API costs
- Can use any GGUF model

**Cons:**
- Requires GPU/CPU resources
- Slower inference than cloud APIs
- Need to manage model downloads

---

## Verifying Your Setup

Run the test script to verify everything works:

```bash
python test_llm_provider.py
```

It will show:
- Which provider is active
- A test dialogue with Aldric
- Any connection errors

---

## Architecture

The system uses an abstract factory pattern:

```
LLMProvider (factory class)
├── GoogleLLMProvider
│   └── Uses google.generativeai
└── LMStudioLLMProvider
    └── Uses requests + OpenAI-compatible API
```

To switch providers at runtime or add a new one:

1. Create a new class inheriting from `BaseLLMProvider`
2. Implement the `generate(prompt: str) -> str` method
3. Add a case in `LLMProvider.get_provider()`

---

## Troubleshooting

### "Could not connect to LM Studio"
- Make sure LM Studio is running
- Check that the port (default 1234) matches your config
- Verify `LMSTUDIO_HOST` is correct (use "localhost" for local)

### Google API key errors
- Verify the API key in `config.py`
- Check that the key is enabled for the Generative AI API
- Make sure you're not exceeding rate limits

### Slow responses
- Google: Check your internet connection
- LM Studio: Model inference is slower on CPU; use GPU if available
