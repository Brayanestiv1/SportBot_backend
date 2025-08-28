from typing import List, Optional
import pymysql
from datetime import datetime
from app.database import get_sync_connection
from app.models.mensaje.MensajeModel import MensajeCreate, MensajeUpdate, MensajeResponse

class MensajeController:
    
    @staticmethod
    def create_mensaje(mensaje: MensajeCreate) -> MensajeResponse:
        """Create a new mensaje"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO mensaje (chatId, tipo, contenido, fechaEnvio) 
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    mensaje.chatId, mensaje.tipo, mensaje.contenido, datetime.now()
                ))
                connection.commit()
                
                mensaje_id = cursor.lastrowid
                return MensajeController.get_mensaje_by_id(mensaje_id)
        finally:
            connection.close()
    
    @staticmethod
    def get_all_mensajes() -> List[MensajeResponse]:
        """Get all mensajes"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM mensaje ORDER BY fechaEnvio DESC"
                cursor.execute(sql)
                result = cursor.fetchall()
                return [MensajeResponse(**row) for row in result]
        finally:
            connection.close()
    
    @staticmethod
    def get_mensaje_by_id(mensaje_id: int) -> Optional[MensajeResponse]:
        """Get mensaje by ID"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM mensaje WHERE id = %s"
                cursor.execute(sql, (mensaje_id,))
                result = cursor.fetchone()
                return MensajeResponse(**result) if result else None
        finally:
            connection.close()
    
    @staticmethod
    def get_mensajes_by_chat(chat_id: int, limit: int = 100, offset: int = 0) -> List[MensajeResponse]:
        """Get mensajes by chat with pagination"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                SELECT * FROM mensaje 
                WHERE chatId = %s 
                ORDER BY fechaEnvio ASC 
                LIMIT %s OFFSET %s
                """
                cursor.execute(sql, (chat_id, limit, offset))
                result = cursor.fetchall()
                return [MensajeResponse(**row) for row in result]
        finally:
            connection.close()
    
    @staticmethod
    def get_recent_mensajes_by_chat(chat_id: int, minutes: int = 60) -> List[MensajeResponse]:
        """Get recent mensajes by chat within specified minutes"""
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
                result = cursor.fetchall()
                return [MensajeResponse(**row) for row in result]
        finally:
            connection.close()
    
    @staticmethod
    def update_mensaje(mensaje_id: int, mensaje: MensajeUpdate) -> Optional[MensajeResponse]:
        """Update mensaje content"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "UPDATE mensaje SET contenido = %s WHERE id = %s"
                cursor.execute(sql, (mensaje.contenido, mensaje_id))
                connection.commit()
                
                if cursor.rowcount > 0:
                    return MensajeController.get_mensaje_by_id(mensaje_id)
                return None
        finally:
            connection.close()
    
    @staticmethod
    def delete_mensaje(mensaje_id: int) -> bool:
        """Delete mensaje"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM mensaje WHERE id = %s"
                cursor.execute(sql, (mensaje_id,))
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()
    
    @staticmethod
    def get_chat_conversation_summary(chat_id: int, last_n_messages: int = 10) -> dict:
        """Get a summary of the last N messages for context"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                SELECT tipo, contenido, fechaEnvio 
                FROM mensaje 
                WHERE chatId = %s 
                ORDER BY fechaEnvio DESC 
                LIMIT %s
                """
                cursor.execute(sql, (chat_id, last_n_messages))
                messages = cursor.fetchall()
                
                # Reverse to get chronological order
                messages.reverse()
                
                return {
                    "chat_id": chat_id,
                    "message_count": len(messages),
                    "conversation": [
                        {
                            "tipo": msg["tipo"],
                            "contenido": msg["contenido"][:200] + "..." if len(msg["contenido"]) > 200 else msg["contenido"],
                            "timestamp": msg["fechaEnvio"].isoformat() if msg["fechaEnvio"] else None
                        }
                        for msg in messages
                    ]
                }
        finally:
            connection.close()
    
    @staticmethod
    def get_chat_statistics(chat_id: int) -> dict:
        """Get statistics for a chat"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                # Total messages
                sql_total = "SELECT COUNT(*) as total FROM mensaje WHERE chatId = %s"
                cursor.execute(sql_total, (chat_id,))
                total_result = cursor.fetchone()
                
                # Messages by type
                sql_by_type = """
                SELECT tipo, COUNT(*) as count 
                FROM mensaje 
                WHERE chatId = %s 
                GROUP BY tipo
                """
                cursor.execute(sql_by_type, (chat_id,))
                by_type_result = cursor.fetchall()
                
                # First and last message dates
                sql_dates = """
                SELECT MIN(fechaEnvio) as first_message, MAX(fechaEnvio) as last_message
                FROM mensaje 
                WHERE chatId = %s
                """
                cursor.execute(sql_dates, (chat_id,))
                dates_result = cursor.fetchone()
                
                return {
                    "chat_id": chat_id,
                    "total_messages": total_result["total"] if total_result else 0,
                    "messages_by_type": {row["tipo"]: row["count"] for row in by_type_result},
                    "first_message": dates_result["first_message"].isoformat() if dates_result and dates_result["first_message"] else None,
                    "last_message": dates_result["last_message"].isoformat() if dates_result and dates_result["last_message"] else None
                }
        finally:
            connection.close()