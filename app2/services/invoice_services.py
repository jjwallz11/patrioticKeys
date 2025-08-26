# app2/services/invoice_services.py

from fastapi import HTTPException
from utils.qb import (
    get_or_create_today_invoice,
    append_invoice_line,
    get_item_id_by_name,
)
from utils.session import get_current_qb_customer

async def add_job_to_invoice(
    description: str,
    qty: float,
    rate: float,
    item_name: str,
    access_token: str,
    realm_id: str,
    session_id: str,
):
    customer_id = get_current_qb_customer(session_id, access_token, realm_id)
    if not customer_id:
        raise HTTPException(status_code=400, detail="No QuickBooks customer selected.")

    item_id = await get_item_id_by_name(item_name, access_token, realm_id)
    invoice = await get_or_create_today_invoice(customer_id, access_token, realm_id)

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