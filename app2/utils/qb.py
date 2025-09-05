# app2/utils/qb/py

import os
import base64
import httpx
from fastapi import HTTPException
from datetime import date
from urllib.parse import quote
from utils.session import get_tokens_and_realm_id
from fastapi import Request
from config import settings

QB_BASE = (
    "https://sandbox-quickbooks.api.intuit.com/v3/company"
    if settings.QB_ENVIRONMENT == "sandbox"
    else "https://quickbooks.api.intuit.com/v3/company"
)

def build_qb_headers(qb_access_token: str) -> dict:
    return {
        "Authorization": f"Bearer {qb_access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }


async def refresh_qb_tokens() -> tuple[str, str]:
    refresh_token = os.getenv("QB_REFRESH_TOKEN")
    client_id = os.getenv("QB_CLIENT_ID")
    client_secret = os.getenv("QB_CLIENT_SECRET")

    if not refresh_token or not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="Missing QuickBooks credentials")

    auth = f"{client_id}:{client_secret}".encode()
    headers = {
        "Authorization": f"Basic {base64.b64encode(auth).decode()}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer",
            headers=headers,
            data=data,
        )

    if response.status_code != 200:
        print("🔴 QuickBooks 400 response:", response.text)
        raise HTTPException(status_code=500, detail=f"QuickBooks refresh failed: {response.text}")

    token_data = response.json()
    return token_data["access_token"], token_data["refresh_token"]


async def search_customers(qb_access_token: str, realm_id: str) -> list[dict]:
    query = "select * from Customer"
    url = f"{QB_BASE}/{realm_id}/query?query={query}"
    
    print("Calling QuickBooks API:", url)
    print("🔸 FULL ACCESS TOKEN:", qb_access_token)
    print("Realm ID:", realm_id)
    print("Query:", query)
    
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url, headers=build_qb_headers(qb_access_token))
            r.raise_for_status()
            json_resp = r.json()
            print("QuickBooks response:", r.json())
            return r.json().get("QueryResponse", {}).get("Customer", [])
        
        except httpx.HTTPStatusError as e:
            print("QuickBooks API error:", e.response.status_code, e.response.text)
            return []


async def get_customer_by_id(customer_id: str, qb_access_token: str, realm_id: str, request: Request):
    url = f"{QB_BASE}/{realm_id}/customer/{customer_id}"
    r = await safe_qb_request("GET", url, request, headers=build_qb_headers(qb_access_token))
    r.raise_for_status()
    c = r.json().get("Customer", {})
    return {
        "id": c.get("Id"),
        "display_name": c.get("DisplayName"),
        "primary_email": (c.get("PrimaryEmailAddr") or {}).get("Address"),
        "primary_phone": (c.get("PrimaryPhone") or {}).get("FreeFormNumber"),
    }


async def create_customer(payload: dict, qb_access_token: str, realm_id: str):
    url = f"{QB_BASE}/{realm_id}/customer"
    body = {
        "DisplayName": payload.get("DisplayName"),
    }
    if email := payload.get("PrimaryEmailAddr"):
        body["PrimaryEmailAddr"] = {"Address": email}
    if phone := payload.get("PrimaryPhone"):
        body["PrimaryPhone"] = {"FreeFormNumber": phone}

    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.post(url, headers=build_qb_headers(qb_access_token), json=body)
    r.raise_for_status()
    c = r.json().get("Customer", {})
    return {
        "id": c.get("Id"),
        "display_name": c.get("DisplayName"),
        "primary_email": (c.get("PrimaryEmailAddr") or {}).get("Address"),
        "primary_phone": (c.get("PrimaryPhone") or {}).get("FreeFormNumber"),
    }


async def create_today_invoice(customer_id: str, qb_access_token: str, realm_id: str):
    today = date.today().isoformat()
    create_url = f"{QB_BASE}/{realm_id}/invoice"
    payload = {
        "Line": [],
        "CustomerRef": {"value": str(customer_id)},
        "TxnDate": today,
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.post(create_url, headers=build_qb_headers(qb_access_token), json=payload)
    r.raise_for_status()

    inv = r.json().get("Invoice", {})
    return {"Id": inv.get("Id"), "DocNumber": inv.get("DocNumber")}


async def get_today_invoice_only(customer_id: str, qb_access_token: str, realm_id: str):
    today = date.today().isoformat()
    q = (
        "select Id, DocNumber, TxnDate, TotalAmt, Balance from Invoice "
        f"where TxnDate = '{today}' "
        f"and CustomerRef = '{customer_id}' "
        "order by MetaData.CreateTime desc"
    )
    query_url = f"{QB_BASE}/{realm_id}/query?query={quote(q)}"

    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(query_url, headers=build_qb_headers(qb_access_token))
    r.raise_for_status()
    invoices = r.json().get("QueryResponse", {}).get("Invoice", []) or []
    if invoices:
        invoice_id = invoices[0]["Id"]
        get_url = f"{QB_BASE}/{realm_id}/invoice/{invoice_id}"
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(get_url, headers=build_qb_headers(qb_access_token))
        r.raise_for_status()
        return r.json().get("Invoice", {})

    return { "Id": None }


async def append_invoice_line(invoice_id: str, description: str, qty: float, rate: float, item_id: str, qb_access_token: str, realm_id: str):
    get_url = f"{QB_BASE}/{realm_id}/invoice/{invoice_id}"
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(get_url, headers=build_qb_headers(qb_access_token))
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
        r = await client.post(update_url, headers=build_qb_headers(qb_access_token), json=payload)
    r.raise_for_status()
    updated = r.json().get("Invoice", {})
    return {"Id": updated.get("Id"), "DocNumber": updated.get("DocNumber")}


async def send_invoice_email(invoice_id: str, qb_access_token: str, realm_id: str):
    url = f"{QB_BASE}/{realm_id}/invoice/{invoice_id}/send"
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.post(url, headers=build_qb_headers(qb_access_token))
    r.raise_for_status()
    return r.json()


async def get_all_qb_items(qb_access_token: str, realm_id: str, request: Request):
    q = "select Id, Name from Item"
    url = f"{QB_BASE}/{realm_id}/query?query={quote(q)}"
    r = await safe_qb_request("GET", url, request, headers=build_qb_headers(qb_access_token))
    r.raise_for_status()
    return r.json().get("QueryResponse", {}).get("Item", [])


async def get_item_id_by_name(name: str, request: Request) -> str:
    qb_access_token, realm_id = get_tokens_and_realm_id(request)
    q = f"select Id, Name from Item where Name = '{name}'"
    url = f"{QB_BASE}/{realm_id}/query?query={quote(q)}"
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(url, headers=build_qb_headers(qb_access_token))
    r.raise_for_status()
    items = r.json().get("QueryResponse", {}).get("Item", [])
    if not items:
        raise ValueError(f"QuickBooks item '{name}' not found.")
    return items[0]["Id"]


async def get_all_invoices_for_customer(customer_id: str, qb_access_token: str, realm_id: str):
    q = (
        "select Id, DocNumber, TxnDate, TotalAmt, Balance, CustomerRef from Invoice "
        f"where CustomerRef = '{customer_id}' "
        "order by TxnDate desc"
    )
    query_url = f"{QB_BASE}/{realm_id}/query?query={quote(q)}"

    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(query_url, headers=build_qb_headers(qb_access_token))
    r.raise_for_status()

    print("📄 QuickBooks all invoices query:", q)
    print("📄 Response:", r.json())

    return r.json().get("QueryResponse", {}).get("Invoice", [])


async def safe_qb_request(
    method: str,
    url: str,
    request: Request,
    headers: dict = None,
    data=None,
    json=None,
    params=None
):
    if headers is None:
        headers = {}

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.request(method, url, headers=headers, data=data, json=json, params=params)

        # Success — return response
        if response.status_code < 400:
            return response

        # Handle token expiration
        if response.status_code == 401:
            error = response.json().get("error_description", "")
            print("🔴 QuickBooks error:", error)

            if "token expired" in error.lower():
                # access token expired → refresh and retry
                await client.get("http://localhost:8000/api/qb-auth/refresh-token", cookies=request.cookies)
                response = await client.request(method, url, headers=headers, data=data, json=json, params=params)
                if response.status_code < 400:
                    return response

            elif "invalid grant" in error.lower():
                raise HTTPException(
                    status_code=401,
                    detail="QuickBooks refresh token is invalid or expired. Please reconnect via /connect-to-qb."
                )

        # Still bad? Raise it
        response.raise_for_status()