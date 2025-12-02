import os
from supabase import create_client, Client

_url = os.environ.get("SUPABASE_URL")
_key = os.environ.get("SUPABASE_KEY")
if not _url or not _key:
    print("Warning: SUPABASE_URL or SUPABASE_KEY environment variables are missing.")
supabase_client: Client = create_client(_url or "", _key or "")


def get_supabase() -> Client:
    """
    Returns the initialized Supabase client instance.

    Returns:
        Client: The Supabase client object for making database requests.
    """
    return supabase_client