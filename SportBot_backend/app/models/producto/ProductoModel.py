from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ProductoBase(BaseModel):
    categoriaId: int
    nombre: str
    descripcion: Optional[str] = None
    talla: Optional[str] = None
    color: Optional[str] = None
    precio: Decimal = Field(..., ge=0)
    stock: int = Field(default=0, ge=0)

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    categoriaId: Optional[int] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    talla: Optional[str] = None
    color: Optional[str] = None
    precio: Optional[Decimal] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)

class ProductoResponse(ProductoBase):
    id: int
    fechaCreacion: datetime
    fechaActualizacion: datetime
    
    class Config:
        from_attributes = True
