from sqlite3 import IntegrityError
import uuid
from datetime import datetime, timedelta, timezone
from apps.api.models.user import User
from apps.api.core.security import create_access_token, create_refresh_token, hash_password, hash_token
from apps.api.core.redis_client import redis_client
from apps.api.core.config import settings
from sqlalchemy.orm import Session
from apps.api.schemas.user import UserCreate


def issues_session(user: User) -> tuple[str, str]:
    """Issues a new access and refresh token for the given user."""
    session_id = str(uuid.uuid4())
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id), session_id)
    
    redis_key = f"refresh:{user.id}:{session_id}"
    
    redis_client.set(
        redis_key,
        hash_token(refresh_token),
        ex=settings.refresh_token_expire_days * 86400  # convert days to seconds,
    )
    
    return access_token, refresh_token

def register(db: Session, data: UserCreate) -> User:
    exisit = db.query(User).filter((User.username == data.username) | (User.email == data.email)).first()
    if exisit:
        raise ValueError("Username or email already exists")
    
    user = User(
        name = data.name,
        username = data.username,
        email = data.email,
        password=hash_password(data.password),
    )
    
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Username or email already exists")
    
    db.refresh(user)
    access_token, refresh_token = issues_session(user)
    return user, access_token, refresh_token
    

def login(db: Session, email: str, password: str) -> tuple[User, str, str]:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise ValueError("Invalid email or password")
    if not hash_password(password) == user.password:
        raise ValueError("Invalid email or password")
    access_token, refresh_token = issues_session(user)
    return user, access_token, refresh_token

def logout():
     pass

def refresh():
    pass