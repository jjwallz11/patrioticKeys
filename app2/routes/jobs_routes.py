# app/routes/jobs_routes.py

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from .auth_routes import get_current_user
from models.users import User
from routes.vehicle_routes import fetch_vehicle_data
from utils.qb import get_or_create_today_invoice, append_invoice_line
from utils.csrf import verify_csrf

router = APIRouter()

class JobPayload(BaseModel):
    customer_id: str = Field(..., description="QuickBooks customer Id")
    vin: str = Field(..., min_length=17, max_length=17)
    service: str = Field("Key creation")
    qty: float = Field(1)
    rate: float = Field(..., gt=0)

@router.post("/locksmith")
async def locksmith_job(payload: JobPayload, request: Request, user: User = Depends(get_current_user)):
    # CSRF (your project enforces on POSTs)
    verify_csrf(request)

    # Decode VIN
    try:
        vehicle = await fetch_vehicle_data(payload.vin)
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to decode VIN")

    # Find or create today's invoice for this customer
    try:
        inv = await get_or_create_today_invoice(payload.customer_id)
        if not inv.get("Id"):
            raise HTTPException(status_code=502, detail="QuickBooks invoice create failed")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=502, detail="QuickBooks service unavailable")

    # Append line with VIN + decoded summary
    summary = f"{payload.service} for {payload.vin}"
    if vehicle.get("year") and vehicle.get("make") and vehicle.get("model"):
        summary += f" ({vehicle['year']} {vehicle['make']} {vehicle['model']})"

    try:
        updated = await append_invoice_line(inv["Id"], summary, payload.qty, payload.rate)
    except Exception:
        raise HTTPException(status_code=502, detail="QuickBooks invoice update failed")

    return {
        "invoice": updated or inv,
        "vehicle": vehicle
    }