"""API dependencies."""

from functools import lru_cache
from macagent.database.interface import DatabaseInterface
from macagent.database.mock_db import MockDatabase
from macagent.vlm.vlm_client import VLMClient
from macagent.vlm.action_executor import ActionExecutor
from macagent.core.config import settings


@lru_cache()
def get_database() -> DatabaseInterface:
    """
    Get database instance.

    Returns mock database by default.
    To use Supabase, set USE_SUPABASE=true in environment.
    """
    use_supabase = settings.supabase_url and settings.supabase_key

    if use_supabase:
        from macagent.database.supabase_db import SupabaseDatabase
        return SupabaseDatabase()
    else:
        return MockDatabase()


@lru_cache()
def get_vlm_client() -> VLMClient:
    """Get VLM client instance."""
    return VLMClient()


@lru_cache()
def get_action_executor() -> ActionExecutor:
    """Get action executor instance."""
    return ActionExecutor()
