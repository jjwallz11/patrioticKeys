# app/schemas/job_schemas.py

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class ServiceType(str, Enum):
    smart_key = "Generate Smart Key"
    high_security = "Generate High Security Transponder key"
    transponder = "Generate Transponder key"

class JobBase(BaseModel):
    customer_id: Optional[str] = Field(None, description="QuickBooks customer Id (optional after first scan)")
    vin: str = Field(..., min_length=17, max_length=17)
    service: ServiceType
    Qty: float = Field(1, gt=0)
    UnitPrice: float = Field(..., gt=0)

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    service: Optional[ServiceType] = None
    Qty: Optional[float] = Field(None, gt=0)
    UnitPrice: Optional[float] = Field(None, gt=0)

class JobResponse(JobBase):
    id: int

    model_config = {
        "from_attributes": True
    }