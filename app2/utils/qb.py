# app/utils/qb.py  (NEW)

import os
import httpx
from datetime import date

QB_BASE = "https://quickbooks.api.intuit.com/v3/company"
QB_REALM_ID = os.getenv("QB_REALM_ID")          # e.g. "1234567890"
QB_TOKEN    = os.getenv("QB_ACCESS_TOKEN")      # Bearer token

def _auth_headers():
    if not (QB_REALM_ID and QB_TOKEN):
        raise RuntimeError("QuickBooks credentials missing: QB_REALM_ID or QB_ACCESS_TOKEN")
    return {
        "Authorization": f"Bearer {QB_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

async def search_customers(query: str = "", limit: int = 25):
    """
    Simple name search. If query is empty, returns first N customers.
    """
    q = f"select * from Customer"
    if query:
        # name contains query (case-insensitive handled by QB)
        q += f" where DisplayName like '%{query}%'"
    q += f" startposition 1 maxresults {max(1, min(limit, 100))}"
    url = f"{QB_BASE}/{QB_REALM_ID}/query?query={httpx.QueryParams({'query': q})['query']}"
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(url, headers=_auth_headers())
    r.raise_for_status()
    data = r.json()
    # Normalize to a simple list
    customers = data.get("QueryResponse", {}).get("Customer", []) or []
    return [
        {
            "id": c["Id"],
            "display_name": c.get("DisplayName"),
            "primary_email": (c.get("PrimaryEmailAddr") or {}).get("Address"),
            "primary_phone": (c.get("PrimaryPhone") or {}).get("FreeFormNumber"),
        }
        for c in customers
    ]

async def get_or_create_today_invoice(customer_id: str):
    """
    Find today's open invoice for the customer; create if not exists.
    Returns minimal invoice dict with Id and DocNumber (when available).
    """
    # Try find an existing invoice for today
    today = date.today().isoformat()
    q = (
        "select Id, DocNumber, TxnDate, TotalAmt, Balance from Invoice "
        f"where CustomerRef = '{customer_id}' and TxnDate = '{today}' and PrivateNote != 'CLOSED' "
        "order by MetaData.CreateTime desc"
    )
    url = f"{QB_BASE}/{QB_REALM_ID}/query?query={httpx.QueryParams({'query': q})['query']}"
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(url, headers=_auth_headers())
    r.raise_for_status()
    invoices = (r.json().get("QueryResponse", {}) or {}).get("Invoice", []) or []
    if invoices:
        return {"Id": invoices[0]["Id"], "DocNumber": invoices[0].get("DocNumber")}

    # Create new invoice for today
    create_url = f"{QB_BASE}/{QB_REALM_ID}/invoice"
    payload = {
        "Line": [],
        "CustomerRef": {"value": str(customer_id)},
        "TxnDate": today,
        # You can add "PrivateNote": "CLOSED" later to mark end-of-day if desired
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.post(create_url, headers=_auth_headers(), json=payload)
    r.raise_for_status()
    inv = r.json().get("Invoice", {})
    return {"Id": inv.get("Id"), "DocNumber": inv.get("DocNumber")}

async def append_invoice_line(invoice_id: str, description: str, qty: float, rate: float):
    """
    Adds a single SalesItem line to an existing invoice by sparse update.
    """
    # Fetch the invoice first to get SyncToken
    get_url = f"{QB_BASE}/{QB_REALM_ID}/invoice/{invoice_id}"
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(get_url, headers=_auth_headers())
    r.raise_for_status()
    inv = r.json().get("Invoice", {})
    sync_token = inv.get("SyncToken", "0")

    update_url = f"{QB_BASE}/{QB_REALM_ID}/invoice?operation=update"
    new_line = {
        "DetailType": "SalesItemLineDetail",
        "Description": description,
        "Amount": round(qty * rate, 2),
        "SalesItemLineDetail": {
            # If you have a specific ItemRef in QB, set it here; else leave None
            # "ItemRef": {"value": "1", "name": "Services"},
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
        r = await client.post(update_url, headers=_auth_headers(), json=payload)
    r.raise_for_status()
    updated = r.json().get("Invoice", {})
    return {"Id": updated.get("Id"), "DocNumber": updated.get("DocNumber")}