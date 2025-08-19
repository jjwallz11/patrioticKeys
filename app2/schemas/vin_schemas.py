# app2/schemas/vin_schemas.py

from pydantic import BaseModel, Field
from typing import Optional


class VehicleResponse(BaseModel):
    vin: str = Field(..., min_length=17, max_length=17)
    make: Optional[str]
    model: Optional[str]
    year: Optional[int]
    bodyType: Optional[str]
    fuelType: Optional[str]
    manufacturer: Optional[str]
    plantCountry: Optional[str]