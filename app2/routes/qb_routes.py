# app/routes/qb_routes.py

from fastapi import APIRouter, Depends, Query
from .auth_routes import get_current_user
from models.users import User
from utils.qb import search_customers

router = APIRouter()

@router.get("/customers")
async def list_customers(
    q: str = Query("", alias="query"),
    limit: int = Query(25, ge=1, le=100),
    user: User = Depends(get_current_user),
):
    return await search_customers(q, limit)