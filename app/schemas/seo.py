from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any

class SEOAnalyzeRequest(BaseModel):
    url: HttpUrl
    keyword: Optional[str] = None

class SEOTitleSuggestion(BaseModel):
    suggested_title: str
    reasoning: str

class SEOMetaSuggestion(BaseModel):
    suggested_meta_description: str
    reasoning: str

class SEOReportResponse(BaseModel):
    url: str
    keyword: Optional[str] = None
    title: Optional[str] = None
    meta_description: Optional[str] = None
    word_count: int = 0
    keyword_density: Optional[float] = None
    readability_score: Optional[float] = None
    readability_feedback: Optional[str] = None
    missing_alt_images: int = 0
    total_images: int = 0
    broken_links: int = 0
    total_links: int = 0
    title_suggestions: List[SEOTitleSuggestion] = []
    meta_suggestions: List[SEOMetaSuggestion] = []
    pagespeed_score: Optional[int] = None
