from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from .client import ClientRead

class InvoiceItemBase(BaseModel):
    name: str
    quantity: int
    unit: str = 'шт.'
    price: float
    total: float

class InvoiceItemCreate(InvoiceItemBase):
    pass

class InvoiceItemRead(InvoiceItemBase):
    id: int
    model_config = {
        "from_attributes": True
    }

class InvoiceBase(BaseModel):
    number: str
    date: date
    client_id: int
    total: float
    status: Optional[str] = 'draft'

class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate]

class InvoiceRead(InvoiceBase):
    id: int
    client: Optional[ClientRead]
    items: List[InvoiceItemRead]
    model_config = {
        "from_attributes": True
    }