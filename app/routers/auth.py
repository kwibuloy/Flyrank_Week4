"""/auth routes: sign up and log in with Supabase Auth."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from supabase_auth.errors import AuthApiError, AuthError

from app.supabase_client import create_supabase_client, supabase

router = APIRouter(prefix="/auth", tags=["Auth"])


class Credentials(BaseModel):
    # Optional here on purpose: a missing field gets our own clear 400 below,
    # not FastAPI's generic 422.
    email: str | None = None
    password: str | None = None


def read_credentials(body: Credentials | None) -> dict | None:
    """Pull email/password from the body; return None if either is missing or blank."""
    if body is None:
        return None
    email = (body.email or "").strip()
    password = body.password or ""
    if not email or not password:
        return None
    return {"email": email, "password": password}


def error(status: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": message})


@router.post("/signup", status_code=201)
def signup(body: Credentials | None = None):
    """Register a new user with Supabase Auth."""
    credentials = read_credentials(body)
    if credentials is None:
        return error(400, "Email and password are required")

    try:
        result = supabase.auth.sign_up(credentials)
    except AuthApiError as err:
        return error(err.status or 400, err.message)
    except AuthError as err:
        return error(400, err.message)

    return {"user": result.user.model_dump(mode="json") if result.user else None}


@router.post("/login")
def login(body: Credentials | None = None):
    """Exchange email/password for an access token and refresh token."""
    credentials = read_credentials(body)
    if credentials is None:
        return error(400, "Email and password are required")

    # A fresh client per login keeps this user's session out of the shared client.
    try:
        result = create_supabase_client().auth.sign_in_with_password(credentials)
    except AuthError:
        return error(401, "Invalid login credentials")

    session, user = result.session, result.user
    return {
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "token_type": session.token_type,
        "expires_in": session.expires_in,
        "user": {"id": user.id, "email": user.email},
    }
