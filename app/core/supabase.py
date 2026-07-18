from supabase import create_client, Client
from app.core.config import get_settings

settings = get_settings()

def get_supabase_client() -> Client:
    """
    Initialize and return the Supabase client.
    Uses the SUPABASE_URL and SUPABASE_KEY from settings.
    """
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_KEY
    if not url or not key:
        raise ValueError("Supabase URL and Key must be set in the environment variables.")
    
    return create_client(url, key)

supabase: Client = get_supabase_client()
