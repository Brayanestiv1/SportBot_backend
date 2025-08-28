from typing import List, Optional
import pymysql
from app.database import get_sync_connection
from app.models.categoria.CategoriaModel import CategoriaCreate, CategoriaUpdate, CategoriaResponse

class CategoriaController:
    
    @staticmethod
    def create_categoria(categoria: CategoriaCreate) -> CategoriaResponse:
        """Create a new categoria"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO categoria (nombre, descripcion) 
                VALUES (%s, %s)
                """
                cursor.execute(sql, (categoria.nombre, categoria.descripcion))
                connection.commit()
                
                # Get the created categoria
                categoria_id = cursor.lastrowid
                return CategoriaController.get_categoria_by_id(categoria_id)
        finally:
            connection.close()
    
    @staticmethod
    def get_all_categorias() -> List[CategoriaResponse]:
        """Get all categorias"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM categoria ORDER BY fechaCreacion DESC"
                cursor.execute(sql)
                result = cursor.fetchall()
                return [CategoriaResponse(**row) for row in result]
        finally:
            connection.close()
    
    @staticmethod
    def get_categoria_by_id(categoria_id: int) -> Optional[CategoriaResponse]:
        """Get categoria by ID"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM categoria WHERE id = %s"
                cursor.execute(sql, (categoria_id,))
                result = cursor.fetchone()
                return CategoriaResponse(**result) if result else None
        finally:
            connection.close()
    
    @staticmethod
    def update_categoria(categoria_id: int, categoria: CategoriaUpdate) -> Optional[CategoriaResponse]:
        """Update categoria"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                # Build dynamic update query
                update_fields = []
                values = []
                
                if categoria.nombre is not None:
                    update_fields.append("nombre = %s")
                    values.append(categoria.nombre)
                
                if categoria.descripcion is not None:
                    update_fields.append("descripcion = %s")
                    values.append(categoria.descripcion)
                
                if not update_fields:
                    return CategoriaController.get_categoria_by_id(categoria_id)
                
                values.append(categoria_id)
                sql = f"UPDATE categoria SET {', '.join(update_fields)} WHERE id = %s"
                cursor.execute(sql, values)
                connection.commit()
                
                return CategoriaController.get_categoria_by_id(categoria_id)
        finally:
            connection.close()
    
    @staticmethod
    def delete_categoria(categoria_id: int) -> bool:
        """Delete categoria"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM categoria WHERE id = %s"
                cursor.execute(sql, (categoria_id,))
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()
