from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.deps import get_db
from identity.profile import get_or_create_user, update_user

router = APIRouter()


class ProfileResponse(BaseModel):
    username: str
    tech_stack: list[str]
    preferences: dict


class ProfileUpdateRequest(BaseModel):
    tech_stack: list[str] | None = None
    preferences: dict | None = None


@router.get("/profile", response_model=ProfileResponse)
def read_profile(db: Session = Depends(get_db)) -> ProfileResponse:
    user = get_or_create_user(db)
    return ProfileResponse(username=user.username, tech_stack=user.tech_stack, preferences=user.preferences)


@router.put("/profile", response_model=ProfileResponse)
def edit_profile(payload: ProfileUpdateRequest, db: Session = Depends(get_db)) -> ProfileResponse:
    user = get_or_create_user(db)
    user = update_user(db, user, tech_stack=payload.tech_stack, preferences=payload.preferences)
    return ProfileResponse(username=user.username, tech_stack=user.tech_stack, preferences=user.preferences)
