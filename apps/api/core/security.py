from jose import jwt, JWTError
from app.core.config import settings

def decode_access_token(token: str) -> str:
    """Returns the user id (sub claim). Raises JWTError on any failure."""
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    return payload["sub"]