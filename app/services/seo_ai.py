from typing import List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.core.llm_factory import get_llm
from app.schemas.seo import SEOTitleSuggestion, SEOMetaSuggestion

class AIRecommendations(BaseModel):
    title_suggestions: List[SEOTitleSuggestion] = Field(
        description="List of suggested titles with reasoning"
    )
    meta_suggestions: List[SEOMetaSuggestion] = Field(
        description="List of suggested meta descriptions with reasoning"
    )

def generate_seo_suggestions(
    title: Optional[str], 
    meta: Optional[str], 
    content: str, 
    keyword: Optional[str]
) -> AIRecommendations:
    llm = get_llm().with_structured_output(AIRecommendations)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert SEO specialist. Given the current title, meta description, and page content, provide suggestions for improving the title and meta description. Focus on readability, CTR, and search intent."),
        ("human", "Current Title: {title}\nCurrent Meta: {meta}\nKeyword targeted: {keyword}\n\nPage Content Snapshot:\n{content}\n\nProvide your improved title and meta description suggestions.")
    ])
    
    # Truncate content to avoid token limits
    content_snapshot = content[:3000] if content else ""
    
    chain = prompt | llm
    
    result = chain.invoke({
        "title": title or "None",
        "meta": meta or "None",
        "keyword": keyword or "None provided",
        "content": content_snapshot
    })
    
    return result
