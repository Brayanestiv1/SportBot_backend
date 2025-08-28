from typing import List, Optional
import pymysql
from app.database import get_sync_connection
from app.models.producto.ProductoModel import ProductoCreate, ProductoUpdate, ProductoResponse

class ProductoController:
    
    @staticmethod
    def create_producto(producto: ProductoCreate) -> ProductoResponse:
        """Create a new producto"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO producto (categoriaId, nombre, descripcion, talla, color, precio, stock) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    producto.categoriaId, producto.nombre, producto.descripcion,
                    producto.talla, producto.color, producto.precio, producto.stock
                ))
                connection.commit()
                
                producto_id = cursor.lastrowid
                return ProductoController.get_producto_by_id(producto_id)
        finally:
            connection.close()
    
    @staticmethod
    def get_all_productos() -> List[ProductoResponse]:
        """Get all productos"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM producto ORDER BY fechaCreacion DESC"
                cursor.execute(sql)
                result = cursor.fetchall()
                return [ProductoResponse(**row) for row in result]
        finally:
            connection.close()
    
    @staticmethod
    def get_producto_by_id(producto_id: int) -> Optional[ProductoResponse]:
        """Get producto by ID"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM producto WHERE id = %s"
                cursor.execute(sql, (producto_id,))
                result = cursor.fetchone()
                return ProductoResponse(**result) if result else None
        finally:
            connection.close()
    
    @staticmethod
    def get_productos_by_categoria(categoria_id: int) -> List[ProductoResponse]:
        """Get productos by categoria"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM producto WHERE categoriaId = %s ORDER BY fechaCreacion DESC"
                cursor.execute(sql, (categoria_id,))
                result = cursor.fetchall()
                return [ProductoResponse(**row) for row in result]
        finally:
            connection.close()
    
    @staticmethod
    def update_producto(producto_id: int, producto: ProductoUpdate) -> Optional[ProductoResponse]:
        """Update producto"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                update_fields = []
                values = []
                
                if producto.categoriaId is not None:
                    update_fields.append("categoriaId = %s")
                    values.append(producto.categoriaId)
                
                if producto.nombre is not None:
                    update_fields.append("nombre = %s")
                    values.append(producto.nombre)
                
                if producto.descripcion is not None:
                    update_fields.append("descripcion = %s")
                    values.append(producto.descripcion)
                
                if producto.talla is not None:
                    update_fields.append("talla = %s")
                    values.append(producto.talla)
                
                if producto.color is not None:
                    update_fields.append("color = %s")
                    values.append(producto.color)
                
                if producto.precio is not None:
                    update_fields.append("precio = %s")
                    values.append(producto.precio)
                
                if producto.stock is not None:
                    update_fields.append("stock = %s")
                    values.append(producto.stock)
                
                if not update_fields:
                    return ProductoController.get_producto_by_id(producto_id)
                
                values.append(producto_id)
                sql = f"UPDATE producto SET {', '.join(update_fields)} WHERE id = %s"
                cursor.execute(sql, values)
                connection.commit()
                
                return ProductoController.get_producto_by_id(producto_id)
        finally:
            connection.close()
    
    @staticmethod
    def delete_producto(producto_id: int) -> bool:
        """Delete producto"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM producto WHERE id = %s"
                cursor.execute(sql, (producto_id,))
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()
