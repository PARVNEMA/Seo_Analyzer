import os
from supabase import create_client, Client
from typing import Dict, Any

def get_supabase_client() -> Client:
    """Initialize and return the Supabase client."""
    url: str = os.getenv("SUPABASE_URL", "")
    key: str = os.getenv("SUPABASE_KEY", "")
    
    if not url or not key:
        print("Warning: SUPABASE_URL or SUPABASE_KEY not set. DB operations will fail.")
        # Returning a dummy client or raising an error depending on strictness
        # For Phase 1 we can just let it fail if not set, or you can handle it gracefully.
        
    return create_client(url, key)

def save_seo_report(report_data: Dict[str, Any]) -> Any:
    """Save the generated SEO report to the Supabase database."""
    try:
        supabase = get_supabase_client()
        # We assume there is a table named 'seo_reports'
        data, count = supabase.table("seo_reports").insert(report_data).execute()
        return data
    except Exception as e:
        print(f"Failed to save report to Supabase: {e}")
        return None
