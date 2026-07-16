from fastapi import APIRouter, HTTPException
from app.schemas.chat import AskRequest, AskResponse
from app.services.rag_service import ask_seo_question

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Ask a question about the SEO of crawled pages.
    """
    try:
        filters = request.filter_metadata or {}
        if request.job_id:
            filters["job_id"] = request.job_id
            
        answer = ask_seo_question(
            query=request.query,
            match_count=request.match_count,
            filter_metadata=filters
        )
        return AskResponse(answer=answer, query=request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
