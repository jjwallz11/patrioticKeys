# app2/routes/qb_auth_routes.py

from fastapi import APIRouter, Request, HTTPException
from starlette.responses import RedirectResponse
import os
import urllib.parse
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import os
import httpx
import base64

router = APIRouter()

@router.get("/connect-to-qb")
async def connect_to_qb():
    client_id = os.getenv("QB_CLIENT_ID")
    redirect_uri = os.getenv("QB_REDIRECT_URI")
    environment = os.getenv("QB_ENVIRONMENT", "sandbox")
    scope = "com.intuit.quickbooks.accounting openid profile email phone address"
    state = "secureRandomStringOrCSRFToken"

    base_auth_url = (
        "https://appcenter.intuit.com/connect/oauth2"
        if environment == "production"
        else "https://sandbox.appcenter.intuit.com/connect/oauth2"
    )

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scope,
        "state": state
    }

    auth_url = f"{base_auth_url}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(auth_url)


@router.get("/callback")
async def qb_callback(request: Request):
    code = request.query_params.get("code")
    realm_id = request.query_params.get("realmId")
    state = request.query_params.get("state")

    if not code or not realm_id:
        raise HTTPException(status_code=400, detail="Missing code or realmId in callback.")

    token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    
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

    async with httpx.AsyncClient() as client:
        r = await client.post(token_url, data=body, headers=headers)

    if r.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Token exchange failed: {r.text}")

    token_data = r.json()
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")

    os.environ["QB_ACCESS_TOKEN"] = access_token
    os.environ["QB_REFRESH_TOKEN"] = refresh_token
    os.environ["QB_REALM_ID"] = realm_id

    return JSONResponse({
        "message": "Authorization successful",
        "realm_id": realm_id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": token_data.get("expires_in"),
    })