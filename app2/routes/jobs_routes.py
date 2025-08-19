# app/routes/jobs_routes.py

from fastapi import APIRouter, HTTPException, Request
from schemas.job_schemas import JobCreate
from services.invoice_services import create_job_invoice
from utils.csrf import verify_csrf
from utils.session import is_user_authenticated
from routes.vehicle_routes import fetch_vehicle_data

router = APIRouter()

@router.post("/locksmith")
async def locksmith_job(payload: JobCreate, request: Request):
    verify_csrf(request)

    if not is_user_authenticated(request):
        raise HTTPException(status_code=403, detail="User not authorized")

    try:
        vehicle = await fetch_vehicle_data(payload.vin)
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to decode VIN")

    try:
        updated_invoice = await create_job_invoice(payload, vehicle, request)
    except HTTPException:
        raise

    return {
        "invoice": updated_invoice,
        "vehicle": vehicle
    }