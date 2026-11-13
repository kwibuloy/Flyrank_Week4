"""Response shapes and error examples, used to document the API in Swagger UI."""

from pydantic import BaseModel, Field


class Error(BaseModel):
    error: str


class LoginUser(BaseModel):
    id: str = Field(examples=["3f1c2b9e-1234-4cde-9abc-0123456789ab"])
    email: str = Field(examples=["test@example.com"])


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field(examples=["bearer"])
    expires_in: int = Field(examples=[3600])
    user: LoginUser


class SignupResponse(BaseModel):
    user: dict | None = Field(description="The Supabase user object")


class Message(BaseModel):
    message: str


class Profile(BaseModel):
    id: str
    email: str | None
    created_at: str | None
    last_sign_in_at: str | None


class Dashboard(BaseModel):
    message: str = Field(examples=["Welcome to your dashboard, test@example.com!"])
    user_id: str


def error_response(description: str, **examples: str) -> dict:
    """An OpenAPI response entry for {"error": ...} bodies, with named examples."""
    return {
        "model": Error,
        "description": description,
        "content": {
            "application/json": {
                "examples": {name: {"value": {"error": msg}} for name, msg in examples.items()}
            }
        },
    }


BAD_REQUEST = {
    400: error_response(
        "Email or password missing, or body is not valid JSON",
        missing="Email and password are required",
        invalid_json="Request body must be valid JSON",
    )
}

UNAUTHORIZED = {
    401: error_response(
        "Missing, malformed, invalid or expired token",
        missing="Access token required",
        invalid="Invalid or expired token",
    )
}
