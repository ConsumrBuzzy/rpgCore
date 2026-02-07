"""
Model Factory: Singleton for Large Language Model Management

This module provides a unified interface for creating Pydantic AI models
with shared network resources (httpx.AsyncClient) and persistent 'keep_alive'
settings to prevent model unloading/reloading (The "Iron Frame" Workflow).
"""

import os
import httpx
from pydantic_ai.models.openai import OpenAIModel

# Singleton client for persistent connections
# increased timeout to handle long-running generations
_SHARED_CLIENT = httpx.AsyncClient(timeout=120.0)

def get_model(model_name: str = "llama3.2:1b", temperature: float = 0.1) -> OpenAIModel:
    """
    Get a configured OpenAIModel instance sharing the global HTTP client.
    
    Args:
        model_name: Name of the Ollama model to use.
        temperature: Sampling temperature (0.1 for logic, 0.8 for creative).
        
    Returns:
        Configured OpenAIModel instance.
    """
    # Ensure environment is set up for local Ollama
    if 'OLLAMA_BASE_URL' not in os.environ:
        os.environ['OLLAMA_BASE_URL'] = 'http://localhost:11434'
        
    os.environ["OPENAI_BASE_URL"] = f"{os.environ['OLLAMA_BASE_URL']}/v1"
    os.environ["OPENAI_API_KEY"] = "ollama"
    
    # We rely on Env vars for configuration as Model logic doesn't accept them directly in this version
    return OpenAIModel(model_name)

def get_common_model_settings(temperature: float = 0.1) -> dict:
    """
    Return standard generation settings.
    """
    return {
        "temperature": temperature,
        "max_tokens": 1024,
        # Ollama specific extra_body
        "extra_body": {
            "keep_alive": -1 # Keep model in memory indefinitely
        }
    }
