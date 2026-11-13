"""/protected routes: every route here runs only after require_auth has verified the token."""

from fastapi import APIRouter, Depends

from app.dependencies import AuthContext, require_auth

router = APIRouter(
    prefix="/protected",
    tags=["Protected"],
    dependencies=[Depends(require_auth)],
)


def iso(value) -> str | None:
    return value.isoformat() if value else None


@router.get("/profile")
def profile(auth: AuthContext = Depends(require_auth)):
    """The verified user's account details."""
    user = auth.user
    return {
        "id": user.id,
        "email": user.email,
        "created_at": iso(user.created_at),
        "last_sign_in_at": iso(user.last_sign_in_at),
    }


@router.get("/dashboard")
def dashboard(auth: AuthContext = Depends(require_auth)):
    """A second protected route using the same dependency."""
    return {
        "message": f"Welcome to your dashboard, {auth.user.email}!",
        "user_id": auth.user.id,
    }
