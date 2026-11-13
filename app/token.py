"""Reading the bearer token from a request."""

from fastapi import Request


def extract_bearer_token(request: Request) -> str | None:
    """Read "Authorization: Bearer <token>" and return the token, or None when the
    header is missing, not a Bearer header, or carries no token."""
    header = request.headers.get("authorization")
    if not header:
        return None

    parts = header.split()
    if len(parts) != 2 or parts[0] != "Bearer":
        return None
    return parts[1]
