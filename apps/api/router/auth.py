from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.params import Depends
from pydantic import BaseModel
from apps.api.dependencies.db import get_db
from apps.api.schemas.user import UserLogin, UserOut, UserCreate
from apps.api.service.auth import register as register_user, login as login_user, logout as logout_user, refresh as refresh_user
from sqlalchemy.orm import Session
from apps.api.core.config import settings


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

class LoginResponse(BaseModel):
    user: UserOut
    access_token: str
    refresh_token: str


@router.post("/login", response_model=LoginResponse, status_code=200)
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    try:
        user, access_token, refresh_token = login_user(db, payload.email, payload.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    
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
    
    return {"user": user, "access_token": access_token, "refresh_token": refresh_token}


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


@router.post("/logout", status_code=204)
def logout(request: Request, response: Response):
    
    refresh_token = request.cookies.get("refresh_token")
    print("refresh_token", refresh_token)
    logout_user(refresh_token)
    
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token", path="/auth")
    
    return


@router.post("/refresh", response_model=UserOut, status_code=200)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        user, access_token, refresh_token = refresh_user(refresh_token, db)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

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
        path="/auth",
    )

    return user
