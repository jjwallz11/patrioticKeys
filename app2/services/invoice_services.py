# app2/services/invoice_services.py

from fastapi import HTTPException, Request
from utils.qb import (
    get_today_invoice_only,
    create_today_invoice,
    append_invoice_line,
    get_all_qb_items,
)
from utils.session import get_tokens_and_realm_id, get_current_qb_customer

async def add_job_to_invoice(
    description: str,
    qty: float,
    rate: float,
    item_name: str,
    request: Request,
):
    access_token, realm_id = get_tokens_and_realm_id(request)
    customer_id = get_current_qb_customer(request)

    if not customer_id:
        raise HTTPException(status_code=400, detail="No QuickBooks customer selected.")

    items = await get_all_qb_items(access_token, realm_id, request)
    matching_item = next((item for item in items if item["Name"] == item_name), None)

    if not matching_item:
        raise HTTPException(status_code=400, detail=f"QuickBooks item '{item_name}' not found.")

    item_id = matching_item["Id"]

    invoice = await get_today_invoice_only(customer_id, access_token, realm_id)
    if not invoice:
        invoice = await create_today_invoice(customer_id, access_token, realm_id)

    result = await append_invoice_line(
        invoice_id=invoice["Id"],
        description=description,
        qty=qty,
        rate=rate,
        item_id=item_id,
        access_token=access_token,
        realm_id=realm_id,
    )
    return result