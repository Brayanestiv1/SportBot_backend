from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from decimal import Decimal

class PromocionBase(BaseModel):
    descripcion: str
    descuentoPorcentaje: Decimal = Field(..., ge=0, le=100)
    fechaInicio: date
    fechaFin: date

class PromocionCreate(PromocionBase):
    pass

class PromocionUpdate(BaseModel):
    descripcion: Optional[str] = None
    descuentoPorcentaje: Optional[Decimal] = Field(None, ge=0, le=100)
    fechaInicio: Optional[date] = None
    fechaFin: Optional[date] = None

class PromocionResponse(PromocionBase):
    id: int
    
    class Config:
        from_attributes = True
