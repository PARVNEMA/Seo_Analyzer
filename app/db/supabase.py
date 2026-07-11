from supabase import create_client, Client
from typing import Dict, Any
from app.core.config import get_settings

def get_supabase_client() -> Client:
    """Initialize and return the Supabase client."""
    settings = get_settings()
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_KEY
    
    if not url or not key:
        print("Warning: SUPABASE_URL or SUPABASE key settings not set. DB operations will fail.")
        
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
