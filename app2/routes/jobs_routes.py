# app2/routes/jobs_routes.py

from fastapi import APIRouter, HTTPException, Request
from schemas.job_schemas import JobCreate
from services.invoice_services import add_job_to_invoice
from utils.csrf import verify_csrf
from utils.session import get_current_qb_customer
from routes.vehicle_routes import fetch_vehicle_data

router = APIRouter()

@router.post("/locksmith")
async def locksmith_job(payload: JobCreate, request: Request):
    verify_csrf(request)

    customer_id = get_current_qb_customer(request)
    if not customer_id:
        raise HTTPException(status_code=401, detail="No QuickBooks customer selected")

    try:
        vehicle = await fetch_vehicle_data(payload.vin)
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to decode VIN")

    try:
        updated_invoice = await add_job_to_invoice(
            description=payload.service.value,
            qty=payload.Qty,
            rate=payload.UnitPrice,
            item_name=payload.service.value,
            request=request
        )
    except HTTPException:
        raise

    return {
        "invoice": updated_invoice,
        "vehicle": vehicle
    }