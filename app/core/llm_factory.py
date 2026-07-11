from asyncio.log import logger
from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel
from app.core.config import get_settings

def get_llm(model_name: Optional[str] = None) -> BaseChatModel:
    """
    Returns a configured LangChain Chat Model based on environment variables.
    Supports Groq and Google Gemini.
    """
    settings = get_settings()
    provider = settings.LLM_PROVIDER.lower()
    
    logger.info(f"Initializing LLM provider: {provider} with model: {model_name or 'default'}")
    
    if provider == "groq":
        from langchain_groq import ChatGroq
        model = model_name or settings.GROQ_MODEL
        # Pass the key explicitly to avoid os.environ search issues
        return ChatGroq(model=model, api_key=settings.GROQ_API_KEY)
    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        model = model_name or settings.GEMINI_MODEL
        # Pass the key explicitly to avoid os.environ search issues
        return ChatGoogleGenerativeAI(model=model, google_api_key=settings.GEMINI_API_KEY)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
