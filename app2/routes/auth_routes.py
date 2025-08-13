# app/routes/auth_routes.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError
from pydantic import BaseModel, EmailStr
from models.users import User
from config import settings
from utils.db import get_async_db
from utils.errors import error_400

from utils.auth import (
    verify_password,
    hash_password,
)

from utils.tokens import (
    generate_csrf_token,
    create_access_token,
    decode_access_token,
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/session/login")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/session/login")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalars().first()

    print("📧 Email received:", payload.email)
    print("🔍 User found in DB:", bool(user))
    if user:
        print("🧂 Stored hash:", user.hashed_password)
        print("🔑 Password matches:", verify_password(payload.password, user.hashed_password))
        print("🧪 Comparing raw password:", payload.password)
        print("🧪 Against hash:", user.hashed_password)
        print("🧾 Rehashed password (for comparison):", hash_password(payload.password))

    if not user or not verify_password(payload.password, user.hashed_password):
        error_400("Invalid credentials")

    access_token = create_access_token({"sub": user.email})
    csrf_token = generate_csrf_token()
    secure_cookie = settings.ENVIRONMENT == "production"

    response = JSONResponse(content={
        "message": "Login successful",
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
    })

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="none",
        secure=secure_cookie
    )

    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        samesite="none",
        secure=secure_cookie
    )

    return response


async def get_current_user(request: Request, db: AsyncSession = Depends(get_async_db)) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: missing subject")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@router.get("/session/current")
async def get_current(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }
    

@router.post("/session/logout")
async def logout():
    secure_cookie = settings.ENVIRONMENT == "production"

    response = JSONResponse(content={"message": "Logout successful"})

    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="none",
        secure=secure_cookie
    )
    response.delete_cookie(
        key="csrf_token",
        httponly=False,
        samesite="none",
        secure=secure_cookie
    )

    return response

    
# --- add near other imports ---
from pydantic import BaseModel, field_validator

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    # simple server-side gate; keep it light and let frontend show confirm match
    @field_validator("new_password")
    @classmethod
    def strong_enough(cls, v: str):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return v

@router.post("/session/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
    request: Request = None,   # present for CSRF verify if you want
):
    # If you require CSRF on POSTs, uncomment the next two lines:
    from utils.csrf import verify_csrf
    verify_csrf(request)

    # 1) verify current
    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")

    # 2) disallow reusing the same password
    if verify_password(payload.new_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="New password must be different.")

    # 3) update
    user.hashed_password = hash_password(payload.new_password)
    await db.commit()

    # (Optional) rotate cookies by issuing a new access token + csrf if you want
    # access_token = create_access_token({"sub": user.email})
    # csrf_token = generate_csrf_token()
    # resp = JSONResponse(content={"message": "Password changed"})
    # secure_cookie = settings.ENVIRONMENT == "production"
    # resp.set_cookie("access_token", access_token, httponly=True, samesite="none", secure=secure_cookie)
    # resp.set_cookie("csrf_token", csrf_token, httponly=False, samesite="none", secure=secure_cookie)
    # return resp

    return {"message": "Password changed"}