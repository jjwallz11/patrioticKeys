# app/services/vehicle_services.py

import httpx
from fastapi import HTTPException

NHTSA_API_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"

async def fetch_vehicle_data(vin: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(NHTSA_API_URL.format(vin=vin))
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="NHTSA API is unavailable")
    data = response.json()
    return {item["Variable"]: item["Value"] for item in data.get("Results", []) if item.get("Value")}
