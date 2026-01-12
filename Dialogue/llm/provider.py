"""
LLM provider abstraction supporting multiple backends.
Currently supports:
  - Google Generative AI (google.generativeai)
  - LM Studio (local OpenAI-compatible API)
"""

from abc import ABC, abstractmethod
from typing import Optional
import google.generativeai as genai
import requests
import json
from config import (
    LLM_PROVIDER,
    Vertex_API_KEY,
    LMSTUDIO_HOST,
    LMSTUDIO_PORT,
    LMSTUDIO_MODEL,
)


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response from a prompt."""
        pass


class GoogleLLMProvider(BaseLLMProvider):
    """Google Generative AI provider."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash", api_key: Optional[str] = None):
        """
        Initialize Google LLM provider.
        
        Args:
            model_name: The model to use
            api_key: Optional API key (uses config default if not provided)
        """
        self.model_name = model_name
        self.api_key = api_key or Vertex_API_KEY
        
        # Configure API once
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
    
    def generate(self, prompt: str) -> str:
        """Generate a response from Google Generative AI."""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Google LLM generation failed: {e}")


class LMStudioLLMProvider(BaseLLMProvider):
    """LM Studio local LLM provider (OpenAI-compatible API)."""
    
    def __init__(
        self,
        host: str = LMSTUDIO_HOST,
        port: int = LMSTUDIO_PORT,
        model: str = LMSTUDIO_MODEL,
    ):
        """
        Initialize LM Studio LLM provider.
        
        Args:
            host: Hostname where LM Studio is running
            port: Port where LM Studio API is listening
            model: Model name to use (should match what's loaded in LM Studio)
        """
        self.host = host
        self.port = port
        self.model = model
        self.api_url = f"http://{host}:{port}/v1/chat/completions"
    
    def generate(self, prompt: str) -> str:
        """Generate a response from LM Studio."""
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2048,
                "stream": False,
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except requests.exceptions.ConnectionError:
            raise Exception(
                f"Could not connect to LM Studio at {self.api_url}. "
                f"Make sure LM Studio is running and configured to listen on port {self.port}."
            )
        except requests.exceptions.Timeout:
            raise Exception("LM Studio request timed out. Model may be processing a large prompt.")
        except Exception as e:
            raise Exception(f"LM Studio generation failed: {e}")


class LLMProvider:
    """Factory class for creating the appropriate LLM provider."""
    
    _instance: Optional[BaseLLMProvider] = None
    
    @classmethod
    def get_provider(cls) -> BaseLLMProvider:
        """
        Get or create the configured LLM provider.
        
        Returns:
            A BaseLLMProvider instance (Google or LM Studio)
            
        Raises:
            ValueError: If LLM_PROVIDER is not recognized
        """
        if cls._instance is None:
            if LLM_PROVIDER == "google":
                cls._instance = GoogleLLMProvider()
            elif LLM_PROVIDER == "lmstudio":
                cls._instance = LMStudioLLMProvider()
            else:
                raise ValueError(
                    f"Unknown LLM_PROVIDER: {LLM_PROVIDER}. "
                    f"Must be 'google' or 'lmstudio'."
                )
        
        return cls._instance
    
    @classmethod
    def generate(cls, prompt: str) -> str:
        """
        Generate a response using the configured provider.
        
        Args:
            prompt: The full prompt to send to the LLM
            
        Returns:
            The LLM's response text
        """
        provider = cls.get_provider()
        return provider.generate(prompt)
