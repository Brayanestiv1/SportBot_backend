from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatBase(BaseModel):
    usuarioId: int
    chatId: str
    ultimoMensaje: Optional[str] = None
    totalMensajes: int = 0

class ChatCreate(ChatBase):
    pass

class ChatUpdate(BaseModel):
    ultimoMensaje: Optional[str] = None
    totalMensajes: Optional[int] = None

class ChatResponse(ChatBase):
    id: int
    fechaCreacion: datetime
    fechaActualizcion: datetime  # Note: keeping the typo from the DDL
    
    class Config:
        from_attributes = True
