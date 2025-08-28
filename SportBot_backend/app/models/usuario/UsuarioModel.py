from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UsuarioBase(BaseModel):
    nombre: str
    telefono: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None

class UsuarioResponse(UsuarioBase):
    id: int
    fechaCreacion: datetime
    fechaActualizacion: datetime
    
    class Config:
        from_attributes = True
