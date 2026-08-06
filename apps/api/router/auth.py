from fastapi import APIRouter, HTTPException, Response
from fastapi.params import Depends
from apps.api.dependencies.db import get_db
from apps.api.schemas.user import UserOut, UserCreate
from apps.api.service.auth import register as register_user
from sqlalchemy.orm import Session
from apps.api.core.config import settings


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/register", response_model=UserOut, status_code=201)
def register(
    payload: UserCreate,
    response:Response,
    db: Session = Depends(get_db)
):
    try:
        user, access_token, refresh_token = register_user(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
      secure=settings.environment != "local",
        samesite="lax",
        max_age=60 * 30, 
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
      secure=settings.environment != "local",
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
        path="/auth",       # narrower scope — see note below
    )
    
    return user
