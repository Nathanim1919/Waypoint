import uuid
from sqlalchemy.exc import IntegrityError
from jose import JWTError
from apps.api.models.user import User
from apps.api.core.security import create_access_token, create_refresh_token, decode_token, hash_password, hash_token, verify_password, verify_token_hash
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

def register(db: Session, data: UserCreate) -> tuple[User, str, str]:
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
    if not verify_password(password, user.password):
        raise ValueError("Invalid email or password")
    access_token, refresh_token = issues_session(user)
    return user, access_token, refresh_token

def logout(refresh_token: str):
    if not refresh_token:
        return
    try:
        payload = decode_token(refresh_token)
    except JWTError:
        return
    
    user_id = payload.get("sub")
    session_id = payload.get("sid")
    
    if user_id and session_id:
        redis_client.delete(f"refresh:{user_id}:{session_id}")
     
    
    

def refresh(refresh_token: str, db: Session) -> tuple[User, str, str]:
    if not refresh_token:
        raise ValueError("Refresh token missing")
    
    try:
        payload = decode_token(refresh_token)
    except JWTError:
        raise ValueError("Invalid refresh token")
    
    user_id = payload.get("sub")
    session_id = payload.get("sid")
    
    if payload.get("type") != "refresh":
        raise ValueError("Invalid token type")
    
    if not user_id or not session_id:
        raise ValueError("Invalid refresh token")
    
    redis_key = f"refresh:{user_id}:{session_id}"
    stored_hashed_token = redis_client.get(redis_key)
    

    stored_hashed_token = redis_client.get(redis_key)
    if not stored_hashed_token or not verify_token_hash(refresh_token, stored_hashed_token):
        raise ValueError("Invalid refresh token")
    
    # Issue new tokens
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")
    
    access_token, new_refresh_token = issues_session(user)
    
    # Invalidate the old refresh token
    redis_client.delete(redis_key)
    
    return user, access_token, new_refresh_token