import requests
from typing import List, Optional

class OllamaLLM:
    """
    Simple client for the Ollama LLM API.

    Example:
        >>> llm = OllamaLLM()
        >>> response = llm.generate("What is RAG?")
    """
    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize the OllamaLLM client.

        Args:
            base_url (str): Base URL for the Ollama API.
        """
        self.base_url = base_url

    def generate(self, prompt: str, model: str = "llama2", context: Optional[List[str]] = None) -> str:
        """
        Generate a response from the LLM using the given prompt and context.

        Args:
            prompt (str): User prompt or question.
            model (str): LLM model name (default: "llama2").
            context (Optional[List[str]]): Optional context strings.

        Returns:
            str: LLM-generated response.

        Example:
            >>> llm = OllamaLLM()
            >>> llm.generate("What is RAG?", model="llama2")
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "context": context or []
        }
        response = requests.post(f"{self.base_url}/api/generate", json=payload)
        response.raise_for_status()
        return response.json().get("response", "")
