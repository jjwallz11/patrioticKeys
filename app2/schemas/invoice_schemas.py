# app/schemas/invoices.py

from pydantic import BaseModel, Field


class InvoiceLineBase(BaseModel):
    Description: str = Field(..., description="Full line description for the invoice")
    Qty: float = Field(..., gt=0, description="Quantity of services/items")
    UnitPrice: float = Field(..., gt=0, description="Rate per item/service")


class InvoiceLineCreate(InvoiceLineBase):
    ItemRef: dict = Field(..., description="QuickBooks ItemRef object with 'value' (Item ID) and optional 'name'")


class InvoiceLineResponse(InvoiceLineBase):
    Id: str = Field(..., description="QuickBooks-generated line ID")
    ItemRef: dict = Field(..., description="QuickBooks ItemRef object with 'value' and optional 'name'")

    model_config = {
        "from_attributes": True
    }