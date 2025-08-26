# app2/utils/qb.py

import httpx
from datetime import date
from urllib.parse import quote
from utils.session import session_store

QB_BASE = "https://quickbooks.api.intuit.com/v3/company"


def build_qb_headers(access_token: str) -> dict:
    return {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }


async def search_customers(q: str, limit: int, access_token: str, realm_id: str) -> list[dict]:
    escaped_q = quote(q)
    query = (
        "select * from Customer"
        if not q else
        f"select * from Customer where DisplayName like '%{escaped_q}%'"
    )
    url = f"{QB_BASE}/{realm_id}/query?query={query}&limit={limit}"
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url, headers=build_qb_headers(access_token))
            r.raise_for_status()
            return r.json().get("QueryResponse", {}).get("Customer", [])
        except httpx.HTTPStatusError as e:
            print("QuickBooks API error:", e.response.status_code, e.response.text)
            return []


async def get_customer_by_id(customer_id: str, access_token: str, realm_id: str):
    url = f"{QB_BASE}/{realm_id}/customer/{customer_id}"
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(url, headers=build_qb_headers(access_token))
    r.raise_for_status()
    c = r.json().get("Customer", {})
    return {
        "id": c.get("Id"),
        "display_name": c.get("DisplayName"),
        "primary_email": (c.get("PrimaryEmailAddr") or {}).get("Address"),
        "primary_phone": (c.get("PrimaryPhone") or {}).get("FreeFormNumber"),
    }


async def create_customer(payload: dict, access_token: str, realm_id: str):
    url = f"{QB_BASE}/{realm_id}/customer"
    body = {
        "DisplayName": payload.get("DisplayName"),
    }
    if email := payload.get("PrimaryEmailAddr"):
        body["PrimaryEmailAddr"] = {"Address": email}
    if phone := payload.get("PrimaryPhone"):
        body["PrimaryPhone"] = {"FreeFormNumber": phone}

    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.post(url, headers=build_qb_headers(access_token), json=body)
    r.raise_for_status()
    c = r.json().get("Customer", {})
    return {
        "id": c.get("Id"),
        "display_name": c.get("DisplayName"),
        "primary_email": (c.get("PrimaryEmailAddr") or {}).get("Address"),
        "primary_phone": (c.get("PrimaryPhone") or {}).get("FreeFormNumber"),
    }


async def get_or_create_today_invoice(customer_id: str, access_token: str, realm_id: str):
    today = date.today().isoformat()
    q = (
        "select Id, DocNumber, TxnDate, TotalAmt, Balance from Invoice "
        f"where CustomerRef = '{customer_id}' and TxnDate = '{today}' and PrivateNote != 'CLOSED' "
        "order by MetaData.CreateTime desc"
    )
    query_url = f"{QB_BASE}/{realm_id}/query?query={quote(q)}"
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(query_url, headers=build_qb_headers(access_token))
    r.raise_for_status()
    invoices = r.json().get("QueryResponse", {}).get("Invoice", []) or []
    if invoices:
        invoice_id = invoices[0]["Id"]
        get_url = f"{QB_BASE}/{realm_id}/invoice/{invoice_id}"
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(get_url, headers=build_qb_headers(access_token))
        r.raise_for_status()
        return r.json().get("Invoice", {})

    # Create new invoice
    create_url = f"{QB_BASE}/{realm_id}/invoice"
    payload = {
        "Line": [],
        "CustomerRef": {"value": str(customer_id)},
        "TxnDate": today,
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.post(create_url, headers=build_qb_headers(access_token), json=payload)
    r.raise_for_status()
    inv = r.json().get("Invoice", {})
    return {"Id": inv.get("Id"), "DocNumber": inv.get("DocNumber")}


async def append_invoice_line(invoice_id: str, description: str, qty: float, rate: float, item_id: str, access_token: str, realm_id: str):
    get_url = f"{QB_BASE}/{realm_id}/invoice/{invoice_id}"
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(get_url, headers=build_qb_headers(access_token))
    r.raise_for_status()
    inv = r.json().get("Invoice", {})
    sync_token = inv.get("SyncToken", "0")

    update_url = f"{QB_BASE}/{realm_id}/invoice?operation=update"
    new_line = {
        "DetailType": "SalesItemLineDetail",
        "Description": description,
        "Amount": round(qty * rate, 2),
        "SalesItemLineDetail": {
            "ItemRef": {"value": item_id},
            "Qty": qty,
            "UnitPrice": rate
        }
    }
    payload = {
        "Id": invoice_id,
        "SyncToken": sync_token,
        "Line": (inv.get("Line") or []) + [new_line],
        "sparse": True
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.post(update_url, headers=build_qb_headers(access_token), json=payload)
    r.raise_for_status()
    updated = r.json().get("Invoice", {})
    return {"Id": updated.get("Id"), "DocNumber": updated.get("DocNumber")}


async def send_invoice_email(invoice_id: str, access_token: str, realm_id: str):
    url = f"{QB_BASE}/{realm_id}/invoice/{invoice_id}/send"
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.post(url, headers=build_qb_headers(access_token))
    r.raise_for_status()
    return r.json()


async def get_session_customer(session_id: str):
    key = f"{session_id}:qb_customer"
    return await session_store.get(key)


async def clear_session_customer(session_id: str):
    key = f"{session_id}:qb_customer"
    await session_store.delete(key)


async def get_all_qb_items(access_token: str, realm_id: str):
    q = "select Id, Name from Item"
    url = f"{QB_BASE}/{realm_id}/query?query={quote(q)}"
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(url, headers=build_qb_headers(access_token))
    r.raise_for_status()
    return r.json().get("QueryResponse", {}).get("Item", [])


async def get_item_id_by_name(name: str, access_token: str, realm_id: str) -> str:
    q = f"select Id, Name from Item where Name = '{name}'"
    url = f"{QB_BASE}/{realm_id}/query?query={quote(q)}"
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(url, headers=build_qb_headers(access_token))
    r.raise_for_status()
    items = r.json().get("QueryResponse", {}).get("Item", [])
    if not items:
        raise ValueError(f"QuickBooks item '{name}' not found.")
    return items[0]["Id"]