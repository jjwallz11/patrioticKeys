# app2/utils/session.py

# In-memory session store (non-persistent)
# Example: {"abc123:qb_customer": "456"}
session_store: dict[str, str] = {}

def get_current_qb_customer(session_id: str, access_token: str, realm_id: str) -> str | None:
    return session_store.get(f"{session_id}:qb_customer")

def set_current_qb_customer(customer_id: str, session_id: str, access_token: str, realm_id: str):
    session_store[f"{session_id}:qb_customer"] = customer_id

def reset_qb_customer(session_id: str):
    session_store.pop(f"{session_id}:qb_customer", None)