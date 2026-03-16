from supabase import create_client, Client
from app.core.config import get_settings
from functools import lru_cache

_client: Client | None = None
_admin_client: Client | None = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        s = get_settings()
        _client = create_client(s.supabase_url, s.supabase_key)
    return _client


def get_supabase_admin() -> Client:
    """Client avec service_role — pour opérations admin (upload, suppression)"""
    global _admin_client
    if _admin_client is None:
        s = get_settings()
        _admin_client = create_client(s.supabase_url, s.supabase_service_key)
    return _admin_client
