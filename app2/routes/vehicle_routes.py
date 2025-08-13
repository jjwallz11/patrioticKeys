# app/routes/vehicle_routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from utils.db import get_async_db
from utils.auth import get_current_user
from models.vehicles import Vehicle
from models.users import User
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
        "make": data.get("Make"),
        "model": data.get("Model"),
        "year": int(data.get("Model Year")) if data.get("Model Year") else None,
        "body_type": data.get("Body Class"),
        "fuel_type": data.get("Fuel Type - Primary"),
        "manufacturer": data.get("Manufacturer Name"),
        "plant_country": data.get("Plant Country"),
    }

@router.get("/{vin}")
async def get_vehicle_by_vin(vin: str, db: AsyncSession = Depends(get_async_db), user: User = Depends(get_current_user)):
    if len(vin) != 17:
        raise HTTPException(status_code=400, detail="Invalid VIN format")

    result = await db.execute(select(Vehicle).where(Vehicle.vin == vin))
    vehicle = result.scalar_one_or_none()

    if vehicle:
        return {
            "vin": vehicle.vin,
            "make": vehicle.make,
            "model": vehicle.model,
            "year": vehicle.year,
            "bodyType": vehicle.body_type,
            "fuelType": vehicle.fuel_type,
            "manufacturer": vehicle.manufacturer,
            "plantCountry": vehicle.plant_country,
            "owner": {
                "id": vehicle.owner.id,
                "company": vehicle.owner.company,
                "phone": vehicle.owner.phone,
                "email": vehicle.owner.email,
            } if vehicle.owner else None
        }

    # If not found, fetch from NHTSA and store it
    data = await fetch_vehicle_data(vin)
    new_vehicle = Vehicle(vin=vin, **data)
    db.add(new_vehicle)
    await db.commit()
    await db.refresh(new_vehicle)

    return {
        "vin": new_vehicle.vin,
        "make": new_vehicle.make,
        "model": new_vehicle.model,
        "year": new_vehicle.year,
        "bodyType": new_vehicle.body_type,
        "fuelType": new_vehicle.fuel_type,
        "manufacturer": new_vehicle.manufacturer,
        "plantCountry": new_vehicle.plant_country,
        "owner": None
    }