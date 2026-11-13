"""Supabase client setup and a connection check."""

import os

import httpx
from dotenv import load_dotenv
from supabase import Client, create_client
from supabase.lib.client_options import SyncClientOptions

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing SUPABASE_URL or SUPABASE_KEY in .env")


def _options() -> SyncClientOptions:
    # The server never keeps a session of its own: each request carries its own token.
    return SyncClientOptions(persist_session=False, auto_refresh_token=False)


supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=_options())


def create_supabase_client() -> Client:
    """A fresh client per sign-in, so one user's session never sits in the shared client."""
    return create_client(SUPABASE_URL, SUPABASE_KEY, options=_options())


def check_supabase_connection() -> None:
    """Hit the Auth health endpoint to prove the URL and key actually work."""
    response = httpx.get(
        f"{SUPABASE_URL}/auth/v1/health", headers={"apikey": SUPABASE_KEY}, timeout=10
    )
    if response.status_code != 200:
        raise RuntimeError(f"Supabase health check failed with status {response.status_code}")
