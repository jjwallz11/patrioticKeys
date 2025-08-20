# app2/utils/tokens.py

from itsdangerous import URLSafeTimedSerializer
from config import settings
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException
import secrets

serializer = URLSafeTimedSerializer(settings.JWT_SECRET)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_EXPIRATION_MINUTES))
    to_encode.update({"exp": expire})
    print("🕒 TOKEN EXPIRES AT:", expire.isoformat())
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    

# CSRF Tokens

def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)