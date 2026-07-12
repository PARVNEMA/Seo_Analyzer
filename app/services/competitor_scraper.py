import logging
from typing import Dict, Any
from duckduckgo_search import DDGS

class RateLimitException(Exception):
    pass

def fetch_competitor_data(keyword: str) -> Dict[str, Any]:
    """
    Fetches top organic search results for the given keyword using DuckDuckGo Search.
    """
    if not keyword:
        return {"error": "Keyword not provided."}

    competitors = []
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(keyword, max_results=5))
            
            for result in results:
                competitors.append({
                    "title": result.get("title"),
                    "link": result.get("href"),
                    "snippet": result.get("body")
                })
        
        return {"competitors": competitors}
    except Exception as e:
        # DDGS can raise exceptions on rate limits (e.g. RatelimitException) or network errors
        error_msg = str(e).lower()
        if "rate limit" in error_msg or "ratelimit" in error_msg or "429" in error_msg:
            raise RateLimitException("DuckDuckGo API rate limit hit.")
        return {"error": str(e)}
