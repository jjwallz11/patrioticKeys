# app/routes/vehicle_routes.py

from fastapi import APIRouter, Depends, HTTPException
from .auth_routes import get_current_user
import httpx

router = APIRouter()

NHTSA_API_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"

async def fetch_vehicle_data(vin: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(NHTSA_API_URL.format(vin=vin))
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="NHTSA API is unavailable")

    data = {
        item["Variable"]: item["Value"]
        for item in response.json().get("Results", [])
        if item["Value"]
    }

    return {
        "vin": vin,
        "make": data.get("Make"),
        "model": data.get("Model"),
        "year": int(data.get("Model Year")) if data.get("Model Year") else None,
        "bodyType": data.get("Body Class"),
        "fuelType": data.get("Fuel Type - Primary"),
        "manufacturer": data.get("Manufacturer Name"),
        "plantCountry": data.get("Plant Country"),
    }

@router.get("/{vin}")
async def get_vehicle_by_vin(vin: str, user=Depends(get_current_user)):
    if len(vin) != 17:
        raise HTTPException(status_code=400, detail="Invalid VIN format")

    return await fetch_vehicle_data(vin)