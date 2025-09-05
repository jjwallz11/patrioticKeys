# app2/routes/qb_routes.py

from fastapi import APIRouter, Request, Body, HTTPException
import re
from utils.qb import (
    search_customers,
    create_customer,
    get_today_invoice_only,
    create_today_invoice,
    send_invoice_email,
    get_all_invoices_for_customer,
)
from utils.session import (
    get_session_id,
    set_current_qb_customer,
    get_current_qb_customer,
    reset_qb_customer
)
from utils.csrf import verify_csrf
from services import add_job_to_invoice

router = APIRouter()

# List or search customers
@router.get("/customers")
async def list_customers(request: Request):
    qb_access_token = request.cookies.get("qb_access_token")
    realm_id = request.cookies.get("qb_realm_id")

    if not qb_access_token or not realm_id:
        raise HTTPException(status_code=401, detail="Missing QuickBooks credentials")

    return await search_customers(qb_access_token, realm_id)

# Create a new customer
@router.post("/customers")
async def create_new_customer(request: Request):
    qb_access_token = request.cookies.get("qb_access_token")
    realm_id = request.cookies.get("qb_realm_id")

    if not qb_access_token or not realm_id:
        raise HTTPException(status_code=401, detail="Missing QuickBooks credentials")

    return await create_customer(qb_access_token, realm_id)

# Create or fetch today's invoice, and store selected customer
@router.get("/customers/{customer_id}/invoices/today")
async def check_today_invoice(customer_id: str, request: Request):
    qb_access_token = request.cookies.get("qb_access_token")
    realm_id = request.cookies.get("qb_realm_id")

    if not qb_access_token or not realm_id:
        raise HTTPException(status_code=401, detail="Missing QuickBooks credentials")

    return await get_today_invoice_only(customer_id, qb_access_token, realm_id)


@router.post("/customers/{customer_id}/invoices/today")
async def create_today_invoice_route(customer_id: str, request: Request):
    verify_csrf(request)

    qb_access_token = request.cookies.get("qb_access_token")
    realm_id = request.cookies.get("qb_realm_id")

    if not qb_access_token or not realm_id:
        raise HTTPException(status_code=401, detail="Missing QuickBooks credentials")

    # ✅ Defensive pattern check — QB IDs are usually numeric but might be alphanumeric in future
    qb_id_pattern = re.compile(r"^[a-zA-Z0-9\-]+$")  # basic validation
    if not qb_id_pattern.match(customer_id):
        raise HTTPException(status_code=400, detail="Invalid QuickBooks customer ID format")

    # ✅ Optionally: validate that this ID exists in QuickBooks
    customers = await search_customers(qb_access_token, realm_id)
    matching_customer = next((c for c in customers if c["Id"] == customer_id), None)
    if not matching_customer:
        raise HTTPException(status_code=404, detail="Customer ID not found in QuickBooks")

    # ✅ Safe to proceed
    set_current_qb_customer(customer_id, request)

    return await create_today_invoice(customer_id, qb_access_token, realm_id)

# Add job line item to current invoice
@router.post("/invoices/items")
async def add_invoice_item(payload: dict = Body(...), request: Request = None):
    return await add_job_to_invoice(
        description=payload["description"],
        qty=payload.get("qty", 1),
        rate=payload.get("rate", 0),
        item_name=payload["item_name"],
        request=request
    )

# Get current selected QB customer from session
@router.get("/session-customer")
async def get_session_customer(request: Request):
    customer_id = get_current_qb_customer(request)
    return {"customer_id": customer_id}

# Clear selected customer from session
@router.post("/reset-customer")
async def reset_customer(request: Request):
    verify_csrf(request)
    reset_qb_customer(request)
    return {"message": "Customer reset successful"}

# Send invoice to stored customer
@router.post("/invoices/send")
async def send_invoice_to_customer(request: Request):
    verify_csrf(request)
    qb_access_token = request.cookies.get("qb_access_token")
    realm_id = request.cookies.get("qb_realm_id")

    if not all([qb_access_token, realm_id]):
        raise HTTPException(status_code=401, detail="Missing authentication context.")

    customer_id = get_current_qb_customer(request)
    if not customer_id:
        raise HTTPException(status_code=400, detail="No active QuickBooks customer.")

    invoice = await get_today_invoice_only(customer_id, qb_access_token, realm_id)
    if not invoice:
        invoice = await create_today_invoice(customer_id, qb_access_token, realm_id)
    await send_invoice_email(invoice["Id"], qb_access_token, realm_id)

    return {
        "message": f"Invoice {invoice['DocNumber']} sent to customer {customer_id}"
    }

# Get current invoice for stored session customer
@router.get("/invoice")
async def get_today_invoice(request: Request):
    session_id = get_session_id(request)
    qb_access_token = request.cookies.get("qb_access_token")
    realm_id = request.cookies.get("qb_realm_id")

    if not all([session_id, qb_access_token, realm_id]):
        raise HTTPException(status_code=401, detail="Missing QuickBooks credentials")

    customer_id = get_current_qb_customer(request)
    if not customer_id:
        raise HTTPException(status_code=400, detail="No active customer found in session")

    return await get_today_invoice_only(customer_id, qb_access_token, realm_id)


@router.get("/customers/{customer_id}/invoices")
async def get_all_invoices(customer_id: str, request: Request):
    qb_access_token = request.cookies.get("qb_access_token")
    realm_id = request.cookies.get("qb_realm_id")

    if not qb_access_token or not realm_id:
        raise HTTPException(status_code=401, detail="Missing QuickBooks credentials")

    return await get_all_invoices_for_customer(customer_id, qb_access_token, realm_id)
