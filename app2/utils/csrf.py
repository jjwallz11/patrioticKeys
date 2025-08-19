# app/utils/csrf.py

from fastapi import Request, HTTPException
from urllib.parse import urlparse
import os

# Set this in Railway (Backend service): FRONTEND_ORIGIN=https://surfacecleanfront-production.up.railway.app (except new PK origin)
ALLOWED_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").rstrip("/")

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

def _origin_matches(request: Request) -> bool:
    # Prefer Origin; fall back to Referer
    origin = request.headers.get("origin") or request.headers.get("referer")
    if not origin:
        return False
    try:
        # Normalize to scheme+host (no trailing slash)
        p = urlparse(origin)
        normalized = f"{p.scheme}://{p.netloc}"
        return normalized == ALLOWED_ORIGIN
    except Exception:
        return False

def verify_csrf(request: Request):
    # 1) Skip for safe methods
    if request.method.upper() in SAFE_METHODS:
        return

    # 2) Read tokens
    cookie_token = request.cookies.get("csrf_token")
    header_token = request.headers.get("x-csrf-token")

    # 3) Primary: double‑submit (strict match)
    if cookie_token and header_token and cookie_token == header_token:
        return

    # 4) Fallback: same-origin POST with valid cookie
    #    (covers prod cases where header isn’t attached, but browser sent cookies
    #     and the page came from your allowed frontend)
    if cookie_token and _origin_matches(request):
        return

    # 5) Fail with detail
    detail = "CSRF check failed"
    if not cookie_token and not header_token:
        detail = "CSRF token missing"
    elif cookie_token and not header_token:
        detail = "CSRF header missing"
    elif not cookie_token and header_token:
        detail = "CSRF cookie missing"
    else:
        detail = "CSRF tokens did not match"

    raise HTTPException(status_code=403, detail=detail)