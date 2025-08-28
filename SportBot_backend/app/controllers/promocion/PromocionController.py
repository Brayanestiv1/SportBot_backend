from typing import List, Optional
import pymysql
from app.database import get_sync_connection
from app.models.promocion.PromocionModel import PromocionCreate, PromocionUpdate, PromocionResponse

class PromocionController:
    
    @staticmethod
    def create_promocion(promocion: PromocionCreate) -> PromocionResponse:
        """Create a new promocion"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO promocion (descripcion, descuentoPorcentaje, fechaInicio, fechaFin) 
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    promocion.descripcion, promocion.descuentoPorcentaje,
                    promocion.fechaInicio, promocion.fechaFin
                ))
                connection.commit()
                
                promocion_id = cursor.lastrowid
                return PromocionController.get_promocion_by_id(promocion_id)
        finally:
            connection.close()
    
    @staticmethod
    def get_all_promociones() -> List[PromocionResponse]:
        """Get all promociones"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM promocion ORDER BY fechaInicio DESC"
                cursor.execute(sql)
                result = cursor.fetchall()
                return [PromocionResponse(**row) for row in result]
        finally:
            connection.close()
    
    @staticmethod
    def get_promocion_by_id(promocion_id: int) -> Optional[PromocionResponse]:
        """Get promocion by ID"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM promocion WHERE id = %s"
                cursor.execute(sql, (promocion_id,))
                result = cursor.fetchone()
                return PromocionResponse(**result) if result else None
        finally:
            connection.close()
    
    @staticmethod
    def update_promocion(promocion_id: int, promocion: PromocionUpdate) -> Optional[PromocionResponse]:
        """Update promocion"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                update_fields = []
                values = []
                
                if promocion.descripcion is not None:
                    update_fields.append("descripcion = %s")
                    values.append(promocion.descripcion)
                
                if promocion.descuentoPorcentaje is not None:
                    update_fields.append("descuentoPorcentaje = %s")
                    values.append(promocion.descuentoPorcentaje)
                
                if promocion.fechaInicio is not None:
                    update_fields.append("fechaInicio = %s")
                    values.append(promocion.fechaInicio)
                
                if promocion.fechaFin is not None:
                    update_fields.append("fechaFin = %s")
                    values.append(promocion.fechaFin)
                
                if not update_fields:
                    return PromocionController.get_promocion_by_id(promocion_id)
                
                values.append(promocion_id)
                sql = f"UPDATE promocion SET {', '.join(update_fields)} WHERE id = %s"
                cursor.execute(sql, values)
                connection.commit()
                
                return PromocionController.get_promocion_by_id(promocion_id)
        finally:
            connection.close()
    
    @staticmethod
    def delete_promocion(promocion_id: int) -> bool:
        """Delete promocion"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM promocion WHERE id = %s"
                cursor.execute(sql, (promocion_id,))
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()
