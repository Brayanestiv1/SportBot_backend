from typing import List, Optional
import pymysql
from app.database import get_sync_connection
from app.models.usuario.UsuarioModel import UsuarioCreate, UsuarioUpdate, UsuarioResponse

class UsuarioController:
    
    @staticmethod
    def create_usuario(usuario: UsuarioCreate) -> UsuarioResponse:
        """Create a new usuario"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO usuario (nombre, telefono) 
                VALUES (%s, %s)
                """
                cursor.execute(sql, (usuario.nombre, usuario.telefono))
                connection.commit()
                
                usuario_id = cursor.lastrowid
                return UsuarioController.get_usuario_by_id(usuario_id)
        finally:
            connection.close()
    
    @staticmethod
    def get_all_usuarios() -> List[UsuarioResponse]:
        """Get all usuarios"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM usuario ORDER BY fechaCreacion DESC"
                cursor.execute(sql)
                result = cursor.fetchall()
                return [UsuarioResponse(**row) for row in result]
        finally:
            connection.close()
    
    @staticmethod
    def get_usuario_by_id(usuario_id: int) -> Optional[UsuarioResponse]:
        """Get usuario by ID"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM usuario WHERE id = %s"
                cursor.execute(sql, (usuario_id,))
                result = cursor.fetchone()
                return UsuarioResponse(**result) if result else None
        finally:
            connection.close()
    
    @staticmethod
    def update_usuario(usuario_id: int, usuario: UsuarioUpdate) -> Optional[UsuarioResponse]:
        """Update usuario"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                update_fields = []
                values = []
                
                if usuario.nombre is not None:
                    update_fields.append("nombre = %s")
                    values.append(usuario.nombre)
                
                if usuario.telefono is not None:
                    update_fields.append("telefono = %s")
                    values.append(usuario.telefono)
                
                if not update_fields:
                    return UsuarioController.get_usuario_by_id(usuario_id)
                
                values.append(usuario_id)
                sql = f"UPDATE usuario SET {', '.join(update_fields)} WHERE id = %s"
                cursor.execute(sql, values)
                connection.commit()
                
                return UsuarioController.get_usuario_by_id(usuario_id)
        finally:
            connection.close()
    
    @staticmethod
    def delete_usuario(usuario_id: int) -> bool:
        """Delete usuario"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM usuario WHERE id = %s"
                cursor.execute(sql, (usuario_id,))
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()
