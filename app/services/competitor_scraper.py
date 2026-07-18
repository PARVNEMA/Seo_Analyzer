import logging
from typing import Dict, Any
from duckduckgo_search import DDGS
from tavily import TavilyClient
from dotenv import load_dotenv
import os
load_dotenv()  # Load environment variables from .env file
class RateLimitException(Exception):
    pass

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def fetch_competitor_data(keyword: str) -> Dict[str, Any]:
    """
    Fetches top organic search results for the given keyword using Tavily Search.
    """
    if not keyword:
        return {"error": "Keyword not provided."}

    competitors = []
    try:

        response = tavily_client.search(keyword, max_results=5)
        results = response.get("results", [])
        print(f"Fetched {len(results)} results for keyword: {keyword}")
        for result in results:
                competitors.append({
                    "title": result.get("title"),
                    "link": result.get("url"),
                    "snippet": result.get("content")
                })

        return {"competitors": competitors}
    except Exception as e:
        # Catch exceptions on rate limits or network errors
        error_msg = str(e).lower()
        if "rate limit" in error_msg or "ratelimit" in error_msg or "429" in error_msg:
            raise RateLimitException("Tavily API rate limit hit.")
        return {"error": str(e)}
