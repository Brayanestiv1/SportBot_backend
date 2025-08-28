from pydantic import BaseModel
from typing import Literal
from datetime import datetime

class MensajeBase(BaseModel):
    chatId: int
    tipo: Literal['usuario', 'bot']
    contenido: str

class MensajeCreate(MensajeBase):
    pass

class MensajeUpdate(BaseModel):
    contenido: str

class MensajeResponse(MensajeBase):
    id: int
    fechaEnvio: datetime
    
    class Config:
        from_attributes = True
