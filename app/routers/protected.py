"""/protected routes: need "Authorization: Bearer <token>"."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from supabase_auth.errors import AuthError

from app.supabase_client import supabase
from app.token import extract_bearer_token

router = APIRouter(prefix="/protected", tags=["Protected"])


def iso(value) -> str | None:
    return value.isoformat() if value else None


@router.get("/profile")
def profile(request: Request):
    """Requires a bearer token, and the token is verified with Supabase
    before any user data is returned."""
    token = extract_bearer_token(request)
    if not token:
        return JSONResponse(status_code=401, content={"error": "Access token required"})

    try:
        result = supabase.auth.get_user(token)
    except AuthError:
        result = None
    if result is None or result.user is None:
        return JSONResponse(status_code=401, content={"error": "Invalid or expired token"})

    user = result.user
    return {
        "id": user.id,
        "email": user.email,
        "created_at": iso(user.created_at),
        "last_sign_in_at": iso(user.last_sign_in_at),
    }
