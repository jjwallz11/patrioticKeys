# app2/utils/session.py

from fastapi import Request

# In-memory session store (non-persistent)
# Example: {"abc123:qb_customer": "456", "xyz789:qb_customer": "789"}
session_store: dict[str, str] = {}

def get_session_id(request: Request) -> str:
    return request.cookies.get("session_id") or request.headers.get("X-Session-Id", "")

def set_current_qb_customer(customer_id: str, request: Request):
    session_id = get_session_id(request)
    session_store[f"{session_id}:qb_customer"] = customer_id

def get_current_qb_customer(request: Request) -> str | None:
    session_id = get_session_id(request)
    return session_store.get(f"{session_id}:qb_customer")

def reset_qb_customer(request: Request):
    session_id = get_session_id(request)
    session_store.pop(f"{session_id}:qb_customer", None)