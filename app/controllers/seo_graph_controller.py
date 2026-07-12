import uuid
from typing import Optional, Dict, Any
from fastapi import HTTPException
from app.graph.workflow import seo_graph
from app.graph.state import AgentState

async def execute_seo_graph(url: str, keyword: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes the LangGraph SEO workflow.
    """
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    # Initial state
    initial_state = {
        "url": url,
        "target_keyword": keyword,
        "raw_content": "",
        "technical_metrics": {},
        "on_page_metrics": {},
        "competitor_data": {},
        "content_gap_analysis": {},
        "final_report": {},
        "errors": []
    }

    try:
        # We use stream or invoke to run the graph
        # Since we just want the final result, invoke is easiest.
        final_state = seo_graph.invoke(initial_state, config=config)

        report = final_state.get("final_report", {})
        errors = final_state.get("errors", [])
        
        # Merge errors into report if it doesn't have them
        if "errors" not in report:
            report["errors"] = errors
            
        return report

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute SEO graph: {str(e)}")
