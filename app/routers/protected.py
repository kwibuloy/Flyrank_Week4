"""/protected routes: need "Authorization: Bearer <token>"."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.token import extract_bearer_token

router = APIRouter(prefix="/protected", tags=["Protected"])


@router.get("/profile")
def profile(request: Request):
    """Requires a bearer token. The token is extracted here but not yet verified with Supabase."""
    token = extract_bearer_token(request)
    if not token:
        return JSONResponse(status_code=401, content={"error": "Access token required"})

    return {"message": "Access token received (not yet verified)"}
