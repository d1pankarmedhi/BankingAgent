import os
import logging
from typing import Any

logger = logging.getLogger(__name__)


def get_llm(temperature: float = 0):
    """
    Get configured LLM based on environment variable LLM_PROVIDER.
    
    Args:
        temperature: Temperature setting for LLM (default: 0)
        
    Returns:
        Configured LLM instance
        
    Supported providers:
        - azure_openai: Azure OpenAI (default)
        - gemini: Google Gemini
        - ollama: Ollama (local models)
        - openai: OpenAI
    """
    provider = os.getenv("LLM_PROVIDER", "azure_openai").lower()
    
    logger.info(f"Initializing LLM provider: {provider}")
    
    if provider == "azure_openai":
        return _get_azure_openai(temperature)
    elif provider == "gemini":
        return _get_gemini(temperature)
    elif provider == "ollama":
        return _get_ollama(temperature)
    elif provider == "openai":
        return _get_openai(temperature)
    else:
        logger.warning(f"Unknown provider '{provider}', falling back to azure_openai")
        return _get_azure_openai(temperature)


def _get_azure_openai(temperature: float) -> Any:
    """Configure Azure OpenAI"""
    from langchain_openai import AzureChatOpenAI
    
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    if not all([api_key, endpoint, deployment]):
        raise ValueError(
            "Azure OpenAI requires: AZURE_OPENAI_API_KEY, "
            "AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_DEPLOYMENT_NAME"
        )
    
    logger.info(f"Using Azure OpenAI deployment: {deployment}")
    
    return AzureChatOpenAI(
        azure_deployment=deployment,
        openai_api_version=api_version,
        azure_endpoint=endpoint,
        api_key=api_key,
        temperature=temperature,
    )


def _get_gemini(temperature: float) -> Any:
    """Configure Google Gemini"""
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    api_key = os.getenv("GOOGLE_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-pro")
    
    if not api_key:
        raise ValueError("Google Gemini requires: GOOGLE_API_KEY")
    
    logger.info(f"Using Google Gemini model: {model}")
    
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=temperature,
    )


def _get_ollama(temperature: float) -> Any:
    """Configure Ollama (local)"""
    from langchain_ollama import ChatOllama
    
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama2")
    
    logger.info(f"Using Ollama model: {model} at {base_url}")
    
    return ChatOllama(
        model=model,
        base_url=base_url,
        temperature=temperature,
    )


def _get_openai(temperature: float) -> Any:
    """Configure OpenAI"""
    from langchain_openai import ChatOpenAI
    
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4")
    
    if not api_key:
        raise ValueError("OpenAI requires: OPENAI_API_KEY")
    
    logger.info(f"Using OpenAI model: {model}")
    
    return ChatOpenAI(
        model=model,
        openai_api_key=api_key,
        temperature=temperature,
    )
