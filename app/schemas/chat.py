from pydantic import BaseModel
from typing import Optional, Dict

class AskRequest(BaseModel):
    query: str
    job_id: Optional[str] = None
    match_count: Optional[int] = 5
    filter_metadata: Optional[Dict] = None

class AskResponse(BaseModel):
    answer: str
    query: str
