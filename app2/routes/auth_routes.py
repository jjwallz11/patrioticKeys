# app2/routes/auth_routes.py

from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from pydantic import BaseModel, EmailStr, field_validator
import re
from datetime import timedelta
from config import settings

from utils.tokens import (
    create_access_token,
    decode_access_token,
    generate_csrf_token,
)

from utils.csrf import verify_csrf

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/session/login")

# --- Hardcoded user store (in-memory) ---
USER_STORE = {
    "email": "leeno@pk.com",
    "password": "password",
    "first_name": "Leeno",
    "last_name": "Patriotic",
    "force_change": True,
}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


@router.post("/session/login")
async def login(payload: LoginRequest):
    user = USER_STORE

    if payload.email != user["email"] or payload.password != user["password"]:
        raise HTTPException(status_code=400, detail="Invalid credentials.")

    token_expires = timedelta(days=7) if payload.remember_me else timedelta(hours=12)
    access_token = create_access_token({"sub": user["email"]}, expires_delta=token_expires)
    csrf_token = generate_csrf_token()
    secure_cookie = settings.ENVIRONMENT == "production"
    realm_id = settings.QB_REALM_ID

    response = JSONResponse(content={
        "message": "Login successful",
        "user": {
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "force_change": user["force_change"],
        }
    })

    response.set_cookie(
        key="qb_access_token",
        value=access_token,
        httponly=True,
        samesite="none",
        secure=secure_cookie,
        max_age=int(token_expires.total_seconds())
    )
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        samesite="none",
        secure=secure_cookie,
        max_age=int(token_expires.total_seconds())
    )
    response.set_cookie(
        key="qb_realm_id",
        value=realm_id,
        httponly=True,
        samesite="none",
        secure=secure_cookie,
        max_age=int(token_expires.total_seconds())
    )

    return response


async def get_current_user(request: Request):
    token = request.cookies.get("qb_access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        if not email or email != USER_STORE["email"]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    return USER_STORE


@router.get("/session/current")
async def get_current(user: dict = Depends(get_current_user)):
    return {
        "email": user["email"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "force_change": user["force_change"],
    }


@router.post("/session/logout")
async def logout():
    secure_cookie = settings.ENVIRONMENT == "production"

    response = JSONResponse(content={"message": "Logout successful"})
    response.delete_cookie("qb_access_token", httponly=True, samesite="none", secure=secure_cookie)
    response.delete_cookie("csrf_token", httponly=False, samesite="none", secure=secure_cookie)
    response.delete_cookie("qb_realm_id", httponly=True, samesite="none", secure=secure_cookie)

    return response


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def strong_enough(cls, v: str):
        if len(v) < 10:
            raise ValueError("Password must be at least 10 characters long.")
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must include at least one uppercase letter.")
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must include at least one lowercase letter.")
        if len(re.findall(r'[^A-Za-z0-9]', v)) < 2:
            raise ValueError("Password must include at least two special characters.")
        return v


@router.post("/session/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    user: dict = Depends(get_current_user),
):
    verify_csrf(request)

    if payload.current_password != user["password"]:
        raise HTTPException(status_code=400, detail="Current password is incorrect.")

    if payload.new_password == user["password"]:
        raise HTTPException(status_code=400, detail="New password must be different.")

    user["password"] = payload.new_password
    user["force_change"] = False

    return {"message": "Password changed"}