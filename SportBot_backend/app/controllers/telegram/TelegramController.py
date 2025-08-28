import asyncio
import logging
from typing import Optional
import httpx
from datetime import datetime

from app.models.telegram.TelegramModel import (
    TelegramWebhookRequest, 
    TelegramResponse, 
    TelegramMessage,
    ChatSession
)
from app.controllers.chat.ChatController import ChatController
from app.controllers.usuario.UsuarioController import UsuarioController
from app.models.usuario.UsuarioModel import UsuarioCreate
from app.config import Config

# Configurar logger
logger = logging.getLogger(__name__)

class TelegramController:
    """
    Controlador para manejar la lógica de interacción con Telegram y el LLM
    con persistencia completa en base de datos
    """
    
    def __init__(self):
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.telegram_api_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.chat_controller = ChatController()
        self.usuario_controller = UsuarioController()
        self.active_sessions = {}  # Cache temporal para sesiones activas
        
    async def process_message(self, webhook_data: TelegramWebhookRequest) -> None:
        """Procesa mensajes de Telegram con persistencia completa"""
        try:
            # Extraer el mensaje (puede ser mensaje nuevo o editado)
            message = webhook_data.message or webhook_data.edited_message
            
            if not message or not message.text:
                logger.warning("Mensaje sin texto recibido")
                return
                
            # Obtener información del usuario y chat
            user = message.from_user
            chat = message.chat
            
            if not user:
                logger.warning("Mensaje sin información de usuario")
                return
            
            logger.info(f"Procesando mensaje de {user.first_name} ({user.id}): {message.text}")
            
            # Crear o obtener usuario en la base de datos
            usuario_id = await self._get_or_create_usuario(user)
            
            # Procesar mensaje con el ChatController que maneja la persistencia
            response_result = await self.chat_controller.process_message(
                message=message.text,
                user_id=usuario_id,
                chat_external_id=f"telegram_{chat.id}"
            )
            
            # Extraer la respuesta del bot
            if response_result["status"] == "success":
                response_text = response_result["data"]["reply"]
            else:
                response_text = "🤖 Disculpa, tuve un problema procesando tu mensaje. ¿Podrías intentar de nuevo?"
            
            # Enviar respuesta a Telegram
            await self._send_telegram_message(chat.id, response_text, message.message_id)
            
            # Actualizar sesión temporal (opcional, para cache)
            await self._update_session_cache(user, chat)
            
            logger.info(f"Mensaje procesado exitosamente para usuario {user.id}")
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {str(e)}")
            # Enviar mensaje de error al usuario
            if 'message' in locals() and message and message.chat:
                await self._send_error_message(message.chat.id)
    
    async def _get_or_create_usuario(self, telegram_user) -> int:
        """Obtiene o crea un usuario en la base de datos"""
        try:
            # Buscar usuario existente por nombre (en un caso real usarías un campo telegram_id)
            usuarios = self.usuario_controller.get_all_usuarios()
            
            # Buscar por nombre completo como identificador temporal
            full_name = f"{telegram_user.first_name}"
            if telegram_user.last_name:
                full_name += f" {telegram_user.last_name}"
            
            # Buscar usuario existente
            existing_user = None
            for usuario in usuarios:
                if usuario.nombre == full_name:
                    existing_user = usuario
                    break
            
            if existing_user:
                return existing_user.id
            
            # Crear nuevo usuario
            new_user = UsuarioCreate(
                nombre=full_name,
                telefono=telegram_user.username if telegram_user.username else None
            )
            
            created_user = self.usuario_controller.create_usuario(new_user)
            logger.info(f"Usuario creado: {created_user.nombre} (ID: {created_user.id})")
            
            return created_user.id
            
        except Exception as e:
            logger.error(f"Error obteniendo/creando usuario: {str(e)}")
            # En caso de error, retornar un ID de usuario por defecto o crear uno genérico
            raise
    
    async def _update_session_cache(self, user, chat) -> None:
        """Actualiza el cache de sesiones activas"""
        session_key = f"{user.id}_{chat.id}"
        
        if session_key in self.active_sessions:
            session = self.active_sessions[session_key]
            session.last_activity = datetime.now()
            session.message_count += 1
        else:
            session = ChatSession(
                user_id=user.id,
                chat_id=chat.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            self.active_sessions[session_key] = session
    
    async def _send_telegram_message(self, chat_id: int, text: str, reply_to_message_id: Optional[int] = None) -> bool:
        """Envía mensaje a Telegram"""
        try:
            # Dividir mensajes largos si es necesario
            max_length = 4096  # Límite de Telegram
            if len(text) > max_length:
                # Enviar en múltiples mensajes
                messages = []
                for i in range(0, len(text), max_length):
                    messages.append(text[i:i + max_length])
                
                for i, message_part in enumerate(messages):
                    telegram_response = TelegramResponse(
                        chat_id=chat_id,
                        text=message_part,
                        reply_to_message_id=reply_to_message_id if i == 0 else None
                    )
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"{self.telegram_api_url}/sendMessage",
                            json=telegram_response.dict(exclude_none=True),
                            timeout=30.0
                        )
                        response.raise_for_status()
            else:
                # Mensaje único
                telegram_response = TelegramResponse(
                    chat_id=chat_id,
                    text=text,
                    reply_to_message_id=reply_to_message_id
                )
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.telegram_api_url}/sendMessage",
                        json=telegram_response.dict(exclude_none=True),
                        timeout=30.0
                    )
                    response.raise_for_status()
            
            logger.info(f"Mensaje enviado exitosamente a chat {chat_id}")
            return True
                
        except httpx.TimeoutException:
            logger.error(f"Timeout enviando mensaje a chat {chat_id}")
            return False
        except Exception as e:
            logger.error(f"Error enviando mensaje a Telegram: {str(e)}")
            return False
    
    async def _send_error_message(self, chat_id: int) -> None:
        """Envía un mensaje de error genérico al usuario"""
        error_message = (
            "🚫 Ups! Algo salió mal. Nuestro equipo técnico ya está trabajando en solucionarlo. "
            "Por favor, intenta de nuevo en unos minutos."
        )
        await self._send_telegram_message(chat_id, error_message)
    
    async def cleanup_inactive_sessions(self, max_idle_minutes: int = 30) -> None:
        """Limpia sesiones inactivas para liberar memoria"""
        current_time = datetime.now()
        inactive_sessions = []
        
        for session_key, session in self.active_sessions.items():
            idle_time = (current_time - session.last_activity).total_seconds() / 60
            if idle_time > max_idle_minutes:
                inactive_sessions.append(session_key)
        
        for session_key in inactive_sessions:
            del self.active_sessions[session_key]
            
        if inactive_sessions:
            logger.info(f"Limpiadas {len(inactive_sessions)} sesiones inactivas")
    
    async def get_user_chat_history(self, telegram_user_id: int, limit: int = 10) -> dict:
        """Obtiene el historial de chat de un usuario de Telegram"""
        try:
            # Buscar usuario por telegram_user_id (necesitarías un campo adicional en la BD)
            # Por ahora, usando una búsqueda simple
            usuarios = self.usuario_controller.get_all_usuarios()
            
            # Aquí deberías tener una mejor forma de mapear usuarios de Telegram
            user_chats = []
            for usuario in usuarios:
                chats = self.chat_controller.get_chats_by_usuario(usuario.id)
                for chat in chats:
                    if f"telegram_" in chat.chatId:
                        history = self.chat_controller.get_chat_history(chat.id, limit)
                        user_chats.append({
                            "chat_id": chat.id,
                            "external_chat_id": chat.chatId,
                            "last_message": chat.ultimoMensaje,
                            "total_messages": chat.totalMensajes,
                            "recent_history": [
                                {
                                    "type": msg.tipo,
                                    "content": msg.contenido,
                                    "timestamp": msg.fechaEnvio.isoformat()
                                }
                                for msg in history
                            ]
                        })
            
            return {
                "telegram_user_id": telegram_user_id,
                "chats": user_chats
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo historial: {str(e)}")
            return {
                "telegram_user_id": telegram_user_id,
                "chats": [],
                "error": str(e)
            }