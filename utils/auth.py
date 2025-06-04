# from datetime import datetime, timedelta, timezone
# from typing import Optional
#
# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from jose import JWTError, jwt
# from passlib.context import CryptContext
#
# from database.model import UserInDB, UserPublic
# from core.config import settings
#
# from  database import crud# To get user from DB
#
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
#
#
# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)
#
#
# def get_password_hash(password: str) -> str:
#     return pwd_context.hash(password)
#
#
# # def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
# #     to_encode = data.copy()
# #     if expires_delta:
# #         expire = datetime.now(timezone.utc) + expires_delta
# #     else:
# #         expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
# #     to_encode.update({"exp": expire})
# #     encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
# #     return encoded_jwt
# #
# #
# # async def get_user_from_token(token: str = Depends(oauth2_scheme)) -> Optional[UserInDB]:
# #     credentials_exception = HTTPException(
# #         status_code=status.HTTP_401_UNAUTHORIZED,
# #         detail="Could not validate credentials",
# #         headers={"WWW-Authenticate": "Bearer"},
# #     )
# #     try:
# #         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
# #         username: Optional[str] = payload.get("sub")
# #         if username is None:
# #             raise credentials_exception
# #         token_data = TokenData(username=username)
# #     except JWTError:
# #         raise credentials_exception
# #
# #     # Use the CRUD function to get user by username (which will use the GSI)
# #     user = await crud.get_user_by_username(username=token_data.username)
# #     if user is None:
# #         raise credentials_exception
# #     return user
# #
# #
# # async def get_current_user(user_in_db: UserInDB = Depends(get_user_from_token)) -> UserInDB:
# #     if user_in_db is None:
# #         raise HTTPException(status_code=401, detail="User not found or invalid token")
# #     return user_in_db
# #
# #
# # async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
# #     if current_user.disabled:
# #         raise HTTPException(status_code=400, detail="Inactive user")
# #     return current_user