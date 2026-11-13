"""/public routes: open to everyone, no token needed."""

from fastapi import APIRouter

router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/info")
def info():
    """Public welcome message."""
    return {"message": "Welcome stranger! This info is public."}
