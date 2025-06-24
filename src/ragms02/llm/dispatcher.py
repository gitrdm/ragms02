"""
LLM Dispatcher: Routes LLM requests to the correct provider/model.
Default: Gemini (Google). Supports override for Ollama, OpenAI, etc.
"""
import os
from ragms02.llm.ollama import OllamaLLM
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Registry of supported models/providers
SUPPORTED_MODELS = {
    "gemini-pro": "gemini",
    "llama2": "ollama",
    "gpt-3.5-turbo": "openai",
    # Add more as needed
}

DEFAULT_MODEL = os.environ.get("RAGMS02_DEFAULT_MODEL", "gemini-pro")
OLLAMA_DEFAULT_MODEL = os.environ.get("OLLAMA_DEFAULT_MODEL", "llama2")


def call_gemini(prompt, context=None, model="gemini-pro"):
    if not genai:
        raise ImportError("google-generativeai is not installed.")
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    gemini = genai.GenerativeModel(model)
    response = gemini.generate_content(prompt)
    return response.text

def call_ollama(prompt, context=None, model=None):
    model = model or OLLAMA_DEFAULT_MODEL
    llm = OllamaLLM()
    return llm.generate(prompt, model=model, context=context)

# Add more provider handlers as needed
def dispatch_llm(prompt, context=None, model=None, provider=None):
    """
    Dispatch LLM call to the correct provider/model.
    Defaults to Gemini if not specified.
    """
    model = model or DEFAULT_MODEL
    provider = provider or SUPPORTED_MODELS.get(model, "gemini")
    if provider == "gemini":
        return call_gemini(prompt, context=context, model=model)
    elif provider == "ollama":
        return call_ollama(prompt, context=context, model=model)
    # elif provider == "openai": ...
    else:
        raise ValueError(f"Unsupported provider/model: {provider}/{model}")
