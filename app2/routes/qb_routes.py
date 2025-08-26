# app2/routes/qb_routes.py

from fastapi import APIRouter, Depends, Request, Body, HTTPException, Query
from .auth_routes import get_current_user
from utils.qb import (
    search_customers,
    create_customer,
    clear_session_customer,
    get_or_create_today_invoice,
    send_invoice_email
)
from utils.session import get_session_id, set_current_qb_customer, get_current_qb_customer
from utils.csrf import verify_csrf
from services import add_job_to_invoice

router = APIRouter()

# List or search customers
@router.get("/customers")
async def list_customers(
    request: Request,
    _ = Depends(get_current_user),
):
    access_token = request.cookies.get("access_token")
    realm_id = request.cookies.get("realm_id")

    if not access_token or not realm_id:
        raise HTTPException(status_code=401, detail="Missing QuickBooks credentials")

    return await search_customers(access_token, realm_id)

# Create a new customer
@router.post("/customers")
async def create_new_customer(
    request: Request,
    payload: dict = Body(...),
    _ = Depends(get_current_user),
):
    access_token = request.cookies.get("access_token")
    realm_id = request.cookies.get("realm_id")

    if not access_token or not realm_id:
        raise HTTPException(status_code=401, detail="Missing QuickBooks credentials")

    return await create_customer(payload, access_token, realm_id)

# Create or fetch today's invoice, and store selected customer
@router.post("/customers/{customer_id}/invoices/today")
async def get_or_create_invoice_today(
    customer_id: str,
    request: Request,
    _ = Depends(get_current_user),
):
    verify_csrf(request)
    set_current_qb_customer(customer_id)

    access_token = request.cookies.get("access_token")
    realm_id = request.cookies.get("realm_id")

    if not access_token or not realm_id:
        raise HTTPException(status_code=401, detail="Missing QuickBooks credentials")

    return await get_or_create_today_invoice(customer_id, access_token, realm_id)

# Add job line item to current invoice
@router.post("/invoices/items")
async def add_invoice_item(payload: dict = Body(...)):
    return await add_job_to_invoice(
        description=payload["description"],
        qty=payload.get("qty", 1),
        rate=payload.get("rate", 0),
        item_name=payload["item_id"]
    )

# Get current selected QB customer from session
@router.get("/session-customer")
async def get_session_customer(
    request: Request,
    _ = Depends(get_current_user),
):
    session_id = get_session_id(request)
    key = f"{session_id}:qb_customer"
    customer_id = await request.app.state.session_store.get(key)
    return {"customer_id": customer_id}

# Clear selected customer from session
@router.post("/reset-customer")
async def reset_customer(
    request: Request,
    _ = Depends(get_current_user),
):
    verify_csrf(request)
    session_id = get_session_id(request)
    await clear_session_customer(session_id)
    return {"message": "Customer reset successful"}

# Send invoice to stored customer
@router.post("/invoices/send")
async def send_invoice_to_customer(
    request: Request,
    _ = Depends(get_current_user),
):
    verify_csrf(request)
    access_token = request.cookies.get("access_token")
    realm_id = request.cookies.get("realm_id")

    if not all([access_token, realm_id]):
        raise HTTPException(status_code=401, detail="Missing authentication context.")

    customer_id = get_current_qb_customer(request)
    if not customer_id:
        raise HTTPException(status_code=400, detail="No active QuickBooks customer.")

    invoice = await get_or_create_today_invoice(customer_id, access_token, realm_id)
    await send_invoice_email(invoice["Id"], access_token, realm_id)

    return {
        "message": f"Invoice {invoice['DocNumber']} sent to customer {customer_id}"
    }

# Get current invoice for stored session customer
@router.get("/invoice")
async def get_today_invoice(
    request: Request,
    _ = Depends(get_current_user),
):
    session_id = get_session_id(request)
    access_token = request.cookies.get("access_token")
    realm_id = request.cookies.get("realm_id")

    if not all([session_id, access_token, realm_id]):
        raise HTTPException(status_code=401, detail="Missing QuickBooks credentials")

    customer_id = await request.app.state.session_store.get(f"{session_id}:qb_customer")
    if not customer_id:
        raise HTTPException(status_code=400, detail="No active customer found in session")

    return await get_or_create_today_invoice(customer_id, access_token, realm_id)