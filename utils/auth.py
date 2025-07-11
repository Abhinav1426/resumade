from fastapi.security import APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext

from database.model import UserInDB, UserPublic
from core.config import settings
from datetime import datetime, timedelta, timezone
from  database import crud# To get user from DB

from fastapi import Depends, HTTPException, status, Request, Header

from fastapi import Request
from fastapi import Security

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_jwt_token(user_id: str, expires_minutes: int = None):
    """
    Create a JWT token for the given user_id. Returns (token, expiry_iso_str)
    """
    if expires_minutes is None:
        expires_minutes = getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 60)
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {
        "sub": user_id,
        "exp": expire
    }
    
    secret_key = getattr(settings, "SECRET_KEY", "changeme-super-secret-key")
    algorithm = getattr(settings, "ALGORITHM", "HS256")
    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token, expire.isoformat()


def get_current_user(
    token: str = Security(api_key_header),
    request: Request = None,
    x_bypass_auth: str = Header(None, description="Set to 'true' to bypass authentication (for testing)")
):
    # Bypass authentication if custom header is present and set to 'true'
    bypass = x_bypass_auth or (request.headers.get('x-bypass-auth') if request else None)
    if bypass and bypass.lower() == 'true':
        return {"bypass": True}
    secret_key = getattr(settings, "SECRET_KEY", "changeme-super-secret-key")
    algorithm = getattr(settings, "ALGORITHM", "HS256")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    # Remove 'Bearer ' prefix if present
    if token.lower().startswith('bearer '):
        token = token[7:]
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # Fetch user from DB
    user = crud.get_user_by_id(user_id)
    if not user:
        raise credentials_exception
    return user