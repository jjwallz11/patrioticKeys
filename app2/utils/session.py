# app2/utils/session.py

from fastapi import Request

# In-memory session store (non-persistent)
session_store: dict[str, str] = {}

# Very basic temp storage of selected QB customer
_qb_customer_id: str | None = None

def set_current_qb_customer(customer_id: str):
    global _qb_customer_id
    _qb_customer_id = customer_id

def get_current_qb_customer() -> str | None:
    return _qb_customer_id

def reset_qb_customer():
    global _qb_customer_id
    _qb_customer_id = None
    

def get_session_id(request: Request) -> str:
    return request.cookies.get("session_id") or request.headers.get("X-Session-Id", "")