from typing import List, Optional, Dict
import pymysql
from datetime import datetime
from app.database import get_sync_connection
from app.models.chat.ChatModel import ChatCreate, ChatUpdate, ChatResponse
from app.models.mensaje.MensajeModel import MensajeCreate, MensajeResponse
from app.services.agent import AgentService
from app.services.data_sync import DataSyncService

class ChatController:
    
    def __init__(self):
        self.agent_service = AgentService()
        self.data_sync_service = DataSyncService()
    
    async def process_message(self, message: str, user_id: Optional[int] = None, chat_external_id: Optional[str] = None) -> Dict:
        """Process message using RAG and persist conversation"""
        try:
            # Use RAG to process the query
            response = await self.agent_service.process_query(message, user_id)
            
            # Store conversation in database if user_id provided
            if user_id:
                chat_record = await self._get_or_create_chat(user_id, chat_external_id)
                
                # Store user message
                await self._store_message(
                    chat_id=chat_record['id'],
                    tipo='usuario',
                    contenido=message
                )
                
                # Store bot response
                bot_reply = response.get("reply", "")
                await self._store_message(
                    chat_id=chat_record['id'],
                    tipo='bot',
                    contenido=bot_reply
                )
                
                # Update chat summary
                await self._update_chat_summary(chat_record['id'], message)
            
            return {
                "status": "success",
                "message": "Consulta procesada exitosamente",
                "data": {
                    "reply": response.get("reply", ""),
                    "sources": response.get("sources", []),
                    "relevance_score": response.get("relevance_score", 0.0),
                    "context_used": response.get("context_used", []),
                    "chat_id": chat_record['id'] if user_id else None
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error procesando mensaje: {str(e)}",
                "data": {
                    "reply": "Lo siento, ocurrió un error procesando tu consulta. Por favor intenta nuevamente.",
                    "sources": [],
                    "relevance_score": 0.0
                }
            }
    
    async def _get_or_create_chat(self, user_id: int, chat_external_id: Optional[str] = None) -> Dict:
        """Get existing chat or create new one for user"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                # Try to find existing chat
                if chat_external_id:
                    sql_check = """
                    SELECT * FROM chat 
                    WHERE usuarioId = %s AND chatId = %s 
                    ORDER BY fechaCreacion DESC LIMIT 1
                    """
                    cursor.execute(sql_check, (user_id, chat_external_id))
                else:
                    sql_check = """
                    SELECT * FROM chat 
                    WHERE usuarioId = %s 
                    ORDER BY fechaCreacion DESC LIMIT 1
                    """
                    cursor.execute(sql_check, (user_id,))
                
                chat_record = cursor.fetchone()
                
                if not chat_record:
                    # Create new chat
                    chat_id_external = chat_external_id or f"chat_{user_id}_{int(datetime.now().timestamp())}"
                    sql_insert = """
                    INSERT INTO chat (usuarioId, chatId, ultimoMensaje, totalMensajes, fechaCreacion, fechaActualizcion) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    now = datetime.now()
                    cursor.execute(sql_insert, (user_id, chat_id_external, "", 0, now, now))
                    connection.commit()
                    
                    # Get the created chat
                    new_chat_id = cursor.lastrowid
                    cursor.execute("SELECT * FROM chat WHERE id = %s", (new_chat_id,))
                    chat_record = cursor.fetchone()
                
                return chat_record
        finally:
            connection.close()
    
    async def _store_message(self, chat_id: int, tipo: str, contenido: str) -> int:
        """Store a message in the mensaje table"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO mensaje (chatId, tipo, contenido, fechaEnvio) 
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, (chat_id, tipo, contenido, datetime.now()))
                connection.commit()
                return cursor.lastrowid
        finally:
            connection.close()
    
    async def _update_chat_summary(self, chat_id: int, last_message: str):
        """Update chat with last message and increment message count"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                UPDATE chat 
                SET ultimoMensaje = %s, 
                    totalMensajes = totalMensajes + 2, 
                    fechaActualizcion = %s
                WHERE id = %s
                """
                cursor.execute(sql, (last_message, datetime.now(), chat_id))
                connection.commit()
        finally:
            connection.close()
    
    def get_chat_history(self, chat_id: int, limit: int = 50) -> List[MensajeResponse]:
        """Get chat message history"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                SELECT * FROM mensaje 
                WHERE chatId = %s 
                ORDER BY fechaEnvio ASC 
                LIMIT %s
                """
                cursor.execute(sql, (chat_id, limit))
                messages = cursor.fetchall()
                return [MensajeResponse(**msg) for msg in messages]
        finally:
            connection.close()
    
    def get_recent_chat_history(self, chat_id: int, minutes: int = 60) -> List[MensajeResponse]:
        """Get recent chat messages within specified minutes"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                SELECT * FROM mensaje 
                WHERE chatId = %s 
                AND fechaEnvio >= DATE_SUB(NOW(), INTERVAL %s MINUTE)
                ORDER BY fechaEnvio ASC
                """
                cursor.execute(sql, (chat_id, minutes))
                messages = cursor.fetchall()
                return [MensajeResponse(**msg) for msg in messages]
        finally:
            connection.close()
    
    @staticmethod
    def create_chat(chat: ChatCreate) -> ChatResponse:
        """Create a new chat"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO chat (usuarioId, chatId, ultimoMensaje, totalMensajes, fechaCreacion, fechaActualizcion) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                now = datetime.now()
                cursor.execute(sql, (
                    chat.usuarioId, chat.chatId, chat.ultimoMensaje, 
                    chat.totalMensajes, now, now
                ))
                connection.commit()
                
                chat_id = cursor.lastrowid
                return ChatController.get_chat_by_id(chat_id)
        finally:
            connection.close()
    
    @staticmethod
    def get_all_chats() -> List[ChatResponse]:
        """Get all chats"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM chat ORDER BY fechaCreacion DESC"
                cursor.execute(sql)
                result = cursor.fetchall()
                return [ChatResponse(**row) for row in result]
        finally:
            connection.close()
    
    @staticmethod
    def get_chat_by_id(chat_id: int) -> Optional[ChatResponse]:
        """Get chat by ID"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM chat WHERE id = %s"
                cursor.execute(sql, (chat_id,))
                result = cursor.fetchone()
                return ChatResponse(**result) if result else None
        finally:
            connection.close()
    
    @staticmethod
    def get_chats_by_usuario(usuario_id: int) -> List[ChatResponse]:
        """Get chats by usuario"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM chat WHERE usuarioId = %s ORDER BY fechaCreacion DESC"
                cursor.execute(sql, (usuario_id,))
                result = cursor.fetchall()
                return [ChatResponse(**row) for row in result]
        finally:
            connection.close()
    
    @staticmethod
    def update_chat(chat_id: int, chat: ChatUpdate) -> Optional[ChatResponse]:
        """Update chat"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                update_fields = []
                values = []
                
                if chat.ultimoMensaje is not None:
                    update_fields.append("ultimoMensaje = %s")
                    values.append(chat.ultimoMensaje)
                
                if chat.totalMensajes is not None:
                    update_fields.append("totalMensajes = %s")
                    values.append(chat.totalMensajes)
                
                if update_fields:
                    update_fields.append("fechaActualizcion = %s")
                    values.append(datetime.now())
                    values.append(chat_id)
                    
                    sql = f"UPDATE chat SET {', '.join(update_fields)} WHERE id = %s"
                    cursor.execute(sql, values)
                    connection.commit()
                
                return ChatController.get_chat_by_id(chat_id)
        finally:
            connection.close()
    
    @staticmethod
    def delete_chat(chat_id: int) -> bool:
        """Delete chat and all its messages"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                # Delete messages first (due to foreign key)
                sql_messages = "DELETE FROM mensaje WHERE chatId = %s"
                cursor.execute(sql_messages, (chat_id,))
                
                # Delete chat
                sql_chat = "DELETE FROM chat WHERE id = %s"
                cursor.execute(sql_chat, (chat_id,))
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()