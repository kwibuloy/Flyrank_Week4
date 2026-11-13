"""require_auth: a FastAPI dependency that lets a request through only with a
valid Supabase access token."""

from dataclasses import dataclass

from fastapi import Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase_auth.errors import AuthError
from supabase_auth.types import User

from app.supabase_client import supabase
from app.token import extract_bearer_token

# Registers the "bearerAuth" scheme in the OpenAPI spec, which gives Swagger UI its
# Authorize button and lock icons. auto_error=False: we write our own 401 messages.
bearer_scheme = HTTPBearer(
    scheme_name="bearerAuth",
    bearerFormat="JWT",
    description="Paste the access_token returned by POST /auth/login.",
    auto_error=False,
)


class Unauthorized(Exception):
    """Raised by require_auth; main.py turns it into a 401 {"error": ...} response."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


@dataclass
class AuthContext:
    user: User  # the verified user
    token: str  # the raw access token


def require_auth(
    request: Request,
    _credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> AuthContext:
    token = extract_bearer_token(request)
    if not token:
        raise Unauthorized("Access token required")

    try:
        result = supabase.auth.get_user(token)
    except AuthError:
        result = None
    if result is None or result.user is None:
        raise Unauthorized("Invalid or expired token")

    return AuthContext(user=result.user, token=token)
