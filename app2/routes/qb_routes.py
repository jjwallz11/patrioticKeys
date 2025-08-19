# app/routes/qb_routes.py

from fastapi import APIRouter, Depends, Query, Body, Request
from .auth_routes import get_current_user
from utils.qb import (
    search_customers,
    create_customer,
    clear_session_customer,
    get_or_create_today_invoice,
    get_all_qb_items
)
from utils.session import get_session_id, set_current_qb_customer
from utils.csrf import verify_csrf
from services import add_job_to_invoice

router = APIRouter()

# Used internally by app to search for matching customers
@router.get("/customers")
async def list_customers(
    q: str = Query("", alias="query"),
    limit: int = Query(25, ge=1, le=100),
    _ = Depends(get_current_user),
):
    return await search_customers(q, limit)

# Create a new customer (if app doesn't find one)
@router.post("/customers")
async def create_new_customer(
    payload: dict = Body(...),
    _ = Depends(get_current_user),
):
    return await create_customer(payload)

# Get or create today's invoice and set session customer
@router.post("/customers/{customer_id}/invoices/today")
async def get_or_create_invoice_today(
    customer_id: str,
    request: Request,
    _ = Depends(get_current_user),
):
    verify_csrf(request)
    set_current_qb_customer(customer_id)
    return await get_or_create_today_invoice(customer_id)

@router.get("/qb/items")
async def get_items():
    items = await get_all_qb_items()
    return {"items": items}

# Add line item to invoice (existing or new)
@router.post("/invoices/items")
async def add_invoice_item(
    payload: dict = Body(...),
    _ = Depends(get_current_user),
):
    return await add_job_to_invoice(payload)

# Get current stored customer for session
@router.get("/session-customer")
async def get_session_customer(
    request: Request,
    _ = Depends(get_current_user),
):
    session_id = get_session_id(request)
    key = f"{session_id}:qb_customer"
    customer_id = await request.app.state.session_store.get(key)
    return {"customer_id": customer_id}

# Reset the stored session customer (when finishing a job lot)
@router.post("/reset-customer")
async def reset_customer(
    request: Request,
    _ = Depends(get_current_user),
):
    verify_csrf(request)
    session_id = get_session_id(request)
    await clear_session_customer(session_id)
    return {"message": "Customer reset successful"}