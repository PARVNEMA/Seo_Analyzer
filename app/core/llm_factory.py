import os
from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel

def get_llm(model_name: Optional[str] = None) -> BaseChatModel:
    """
    Returns a configured LangChain Chat Model based on environment variables.
    Supports Groq and Google Gemini.
    """
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    if provider == "groq":
        from langchain_groq import ChatGroq
        # Defaults to a fast Groq model
        model = model_name or os.getenv("GROQ_MODEL", "llama3-8b-8192")
        return ChatGroq(model=model)
    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        # Defaults to a fast Gemini model
        model = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        return ChatGoogleGenerativeAI(model=model)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
