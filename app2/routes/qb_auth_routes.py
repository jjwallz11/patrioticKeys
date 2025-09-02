from fastapi import APIRouter, Request, HTTPException
from starlette.responses import RedirectResponse
import os
import urllib.parse
import httpx
import base64

router = APIRouter()


@router.get("/refresh-token")
async def refresh_qb_access_token():
    refresh_token = os.getenv("QB_REFRESH_TOKEN")
    client_id = os.getenv("QB_CLIENT_ID")
    client_secret = os.getenv("QB_CLIENT_SECRET")

    if not refresh_token or not client_id or not client_secret:
        raise HTTPException(status_code=400, detail="Missing refresh token or credentials")

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
        raise HTTPException(status_code=500, detail=f"Refresh failed: {response.text}")

    token_data = response.json()
    new_qb_access_token = token_data["access_token"]
    new_refresh_token = token_data["refresh_token"]

    # Optional: Log or store these securely
    print("🆕 ACCESS TOKEN:", new_qb_access_token)
    print("🆕 REFRESH TOKEN:", new_refresh_token)

    return {
        "access_token": new_qb_access_token,
        "refresh_token": new_refresh_token
    }
    
    
@router.get("/connect-to-qb")
async def connect_to_qb():
    print("🔁 /connect-to-qb route was hit")
    client_id = os.getenv("QB_CLIENT_ID")
    redirect_uri = os.getenv("QB_REDIRECT_URI")
    scope = "com.intuit.quickbooks.accounting openid profile email phone address"
    state = "secureRandomStringOrCSRFToken"

    base_auth_url = "https://appcenter.intuit.com/connect/oauth2"

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scope,
        "state": state
    }

    auth_url = f"{base_auth_url}?{urllib.parse.urlencode(params)}"
    print("🧪 FULL AUTH URL:", auth_url)

    return RedirectResponse(auth_url)


@router.get("/callback/")
async def qb_callback(request: Request):
    code = request.query_params.get("code")
    realm_id = request.query_params.get("realmId")
    state = request.query_params.get("state")

    if not code or not realm_id:
        raise HTTPException(status_code=400, detail="Missing code or realmId in callback.")

    token_url = "https://sandbox-accounts.platform.intuit.com/oauth2/v1/tokens/bearer"
    
    client_id = os.getenv("QB_CLIENT_ID")
    client_secret = os.getenv("QB_CLIENT_SECRET")
    auth_bytes = f"{client_id}:{client_secret}".encode("utf-8")
    auth_header = base64.b64encode(auth_bytes).decode("utf-8")
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth_header}",
    }
    
    body = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": os.getenv("QB_REDIRECT_URI"),
    }

    print("🚨 Using redirect_uri for token exchange:", os.getenv("QB_REDIRECT_URI"))
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=body, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Token exchange failed: {response.text}")

    token_data = response.json()
    qb_access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")

    response_redirect = RedirectResponse(url=os.getenv("QB_POST_LOGIN_REDIRECT", "/home"))

    response_redirect.set_cookie("qb_access_token", qb_access_token, httponly=True)
    response_redirect.set_cookie("qb_refresh_token", refresh_token, httponly=True)
    response_redirect.set_cookie("qb_realm_id", realm_id, httponly=True)

    return response_redirect