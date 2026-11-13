"""/public routes: open to everyone, no token needed."""

from fastapi import APIRouter

from app.schemas import Message

router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/info", response_model=Message)
def info():
    """Public welcome message."""
    return {"message": "Welcome stranger! This info is public."}
