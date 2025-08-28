# Definir modelo Pydantic para validar payload entrante de Telegram.

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class TelegramUser(BaseModel):
    # Modelo para representar un usuario de Telegram
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None


class TelegramChat(BaseModel):
    # Modelo para representar un chat de Telegram
    id: int
    type: str  # "private", "group", "supergroup", "channel"
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class TelegramMessage(BaseModel):
    # Modelo para representar un mensaje de Telegram
    message_id: int
    from_user: Optional[TelegramUser] = Field(None, alias="from")
    date: int
    chat: TelegramChat
    text: Optional[str] = None
    caption: Optional[str] = None
    
    class Config:
        populate_by_name = True


class TelegramWebhookRequest(BaseModel):
    # Modelo principal para validar el payload del webhook de Telegram
    update_id: int
    message: Optional[TelegramMessage] = None
    edited_message: Optional[TelegramMessage] = None
    callback_query: Optional[Dict[str, Any]] = None
    
    class Config:
        extra = "allow" 

class TelegramResponse(BaseModel):
    # Modelo para las respuestas que se envían a Telegram
    chat_id: int
    text: str
    parse_mode: Optional[str] = "Markdown"
    reply_to_message_id: Optional[int] = None
    disable_web_page_preview: Optional[bool] = True


class ChatSession(BaseModel):
    # Modelo para representar una sesión de chat
    user_id: int
    chat_id: int
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    message_count: int = 0