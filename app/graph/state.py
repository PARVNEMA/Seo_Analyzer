from typing import TypedDict, Optional, List, Dict, Any

class AgentState(TypedDict):
    url: Optional[str]
    raw_content: str
    target_keyword: Optional[str]
    technical_metrics: Dict[str, Any]
    on_page_metrics: Dict[str, Any]
    competitor_data: Dict[str, Any]
    content_gap_analysis: Dict[str, Any]
    final_report: Dict[str, Any]
    errors: List[str]
