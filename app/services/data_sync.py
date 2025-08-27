from typing import List, Dict, Optional
import asyncio
from datetime import datetime
from app.database import get_sync_connection
from app.services.qdrant import QdrantService
from app.services.embedding import EmbeddingService
import logging

logger = logging.getLogger(__name__)

class DataSyncService:
    """Service for synchronizing MySQL data with Qdrant vector database"""
    
    def __init__(self):
        self.qdrant_service = QdrantService()
        self.embedding_service = EmbeddingService()
    
    async def sync_all_data(self) -> Dict:
        """Perform complete data synchronization from MySQL to Qdrant"""
        try:
            logger.info("Starting complete data synchronization")
            
            # Initialize Qdrant collection if not exists
            self.qdrant_service.create_collection_if_not_exists()
            
            # Sync all data types
            productos_count = await self._sync_productos()
            categorias_count = await self._sync_categorias()
            promociones_count = await self._sync_promociones()
            
            total_synced = productos_count + categorias_count + promociones_count
            
            logger.info(f"Synchronization completed. Total documents: {total_synced}")
            
            return {
                "status": "success",
                "message": "Sincronización completa exitosa",
                "synced_count": total_synced,
                "details": {
                    "productos": productos_count,
                    "categorias": categorias_count,
                    "promociones": promociones_count
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error during synchronization: {str(e)}")
            return {
                "status": "error",
                "message": f"Error en sincronización: {str(e)}",
                "synced_count": 0,
                "errors": [str(e)]
            }
    
    async def sync_incremental(self, last_sync_time: Optional[datetime] = None) -> Dict:
        """Perform incremental synchronization based on modification timestamps"""
        try:
            logger.info("Starting incremental synchronization")
            
            if not last_sync_time:
                # If no timestamp provided, sync last 24 hours
                from datetime import timedelta
                last_sync_time = datetime.now() - timedelta(hours=24)
            
            # Sync only modified data
            productos_count = await self._sync_productos_incremental(last_sync_time)
            categorias_count = await self._sync_categorias_incremental(last_sync_time)
            promociones_count = await self._sync_promociones_incremental(last_sync_time)
            
            total_synced = productos_count + categorias_count + promociones_count
            
            return {
                "status": "success",
                "message": "Sincronización incremental exitosa",
                "synced_count": total_synced,
                "last_sync_time": last_sync_time.isoformat(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error during incremental sync: {str(e)}")
            return {
                "status": "error",
                "message": f"Error en sincronización incremental: {str(e)}",
                "synced_count": 0,
                "errors": [str(e)]
            }
    
    async def _sync_productos(self) -> int:
        """Sync all productos to Qdrant"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                SELECT p.*, c.nombre as categoria_nombre,
                       GROUP_CONCAT(DISTINCT CONCAT(pr.descripcion, ':', pr.descuentoPorcentaje, '%') SEPARATOR ' | ') as promociones_activas
                FROM producto p 
                LEFT JOIN categoria c ON p.categoriaId = c.id
                LEFT JOIN promocionProducto pp ON p.id = pp.productoId
                LEFT JOIN promocion pr ON pp.promocionId = pr.id 
                    AND pr.fechaInicio <= CURDATE() 
                    AND pr.fechaFin >= CURDATE()
                GROUP BY p.id, p.nombre, p.descripcion, p.precio, p.stock, p.talla, p.color, p.categoriaId, c.nombre
                """
                cursor.execute(sql)
                productos = cursor.fetchall()
                
                synced_count = 0
                for producto in productos:
                    # Create searchable text content
                    content = self._create_producto_content(producto)
                    
                    # Generate embedding
                    embedding = await self.embedding_service.generate_embedding(content)
                    
                    doc_id = int(producto['id'])
                    
                    # Store in Qdrant
                    await self.qdrant_service.upsert_document(
                        doc_id=doc_id,
                        content=content,
                        embedding=embedding,
                        metadata={
                            "type": "producto",
                            "id": producto['id'],
                            "nombre": producto['nombre'],
                            "categoria": producto.get('categoria_nombre', ''),
                            "categoria_id": producto['categoriaId'],
                            "precio": float(producto['precio']) if producto['precio'] else 0.0,
                            "disponible": producto['stock'] > 0,  # Based on stock availability
                            "descripcion": producto.get('descripcion', ''),
                            "talla": producto.get('talla', ''),
                            "color": producto.get('color', ''),
                            "stock": producto['stock'],
                            "promociones_activas": producto.get('promociones_activas', '') or ''
                        }
                    )
                    synced_count += 1
                
                return synced_count
                
        finally:
            connection.close()
    
    async def _sync_categorias(self) -> int:
        """Sync all categorias to Qdrant"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM categoria"
                cursor.execute(sql)
                categorias = cursor.fetchall()
                
                synced_count = 0
                for categoria in categorias:
                    content = self._create_categoria_content(categoria)
                    embedding = await self.embedding_service.generate_embedding(content)
                    
                    doc_id = int(categoria['id']) + 1000000
                    
                    await self.qdrant_service.upsert_document(
                        doc_id=doc_id,
                        content=content,
                        embedding=embedding,
                        metadata={
                            "type": "categoria",
                            "id": categoria['id'],
                            "nombre": categoria['nombre'],
                            "descripcion": categoria.get('descripcion', '')
                        }
                    )
                    synced_count += 1
                
                return synced_count
                
        finally:
            connection.close()
    
    async def _sync_promociones(self) -> int:
        """Sync all promociones to Qdrant with associated products"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                SELECT pr.*, 
                       GROUP_CONCAT(DISTINCT p.nombre SEPARATOR ', ') as productos_nombres,
                       GROUP_CONCAT(DISTINCT CONCAT(p.nombre, ' ($', p.precio, ')') SEPARATOR ', ') as productos_detalles,
                       COUNT(DISTINCT p.id) as total_productos
                FROM promocion pr
                LEFT JOIN promocionProducto pp ON pr.id = pp.promocionId
                LEFT JOIN producto p ON pp.productoId = p.id
                GROUP BY pr.id
                """
                cursor.execute(sql)
                promociones = cursor.fetchall()
                
                synced_count = 0
                for promocion in promociones:
                    content = self._create_promocion_content(promocion)
                    embedding = await self.embedding_service.generate_embedding(content)
                    
                    from datetime import date
                    today = date.today()
                    is_active = (promocion['fechaInicio'] <= today <= promocion['fechaFin'])
                    
                    doc_id = int(promocion['id']) + 2000000
                    
                    await self.qdrant_service.upsert_document(
                        doc_id=doc_id,
                        content=content,
                        embedding=embedding,
                        metadata={
                            "type": "promocion",
                            "id": promocion['id'],
                            "descripcion": promocion['descripcion'],
                            "descuento": float(promocion['descuentoPorcentaje']) if promocion['descuentoPorcentaje'] else 0.0,
                            "fecha_inicio": promocion['fechaInicio'].isoformat() if promocion['fechaInicio'] else None,
                            "fecha_fin": promocion['fechaFin'].isoformat() if promocion['fechaFin'] else None,
                            "activa": is_active,
                            "productos_nombres": promocion.get('productos_nombres', '') or '',
                            "productos_detalles": promocion.get('productos_detalles', '') or '',
                            "total_productos": promocion.get('total_productos', 0) or 0
                        }
                    )
                    synced_count += 1
                
                return synced_count
                
        finally:
            connection.close()

    def _create_producto_content(self, producto: Dict) -> str:
        """Create searchable content for producto"""
        parts = [
            f"Producto: {producto['nombre']}",
            f"Descripción: {producto.get('descripcion', '')}" if producto.get('descripcion') else "",
            f"Categoría: {producto.get('categoria_nombre', '')}" if producto.get('categoria_nombre') else "",
            f"Precio: ${producto['precio']}" if producto['precio'] else "",
            f"Talla: {producto.get('talla', '')}" if producto.get('talla') else "",
            f"Color: {producto.get('color', '')}" if producto.get('color') else "",
            f"Stock: {producto['stock']} unidades" if producto['stock'] else "",
            f"Disponible: {'Sí' if producto['stock'] > 0 else 'No'}"
        ]
        
        if producto.get('promociones_activas'):
            parts.append(f"Promociones activas: {producto['promociones_activas']}")
        
        return " | ".join([p for p in parts if p])

    def _create_categoria_content(self, categoria: Dict) -> str:
        """Create searchable content for categoria"""
        parts = [
            f"Categoría: {categoria['nombre']}",
            f"Descripción: {categoria.get('descripcion', '')}" if categoria.get('descripcion') else ""
        ]
        return " | ".join([p for p in parts if p])
    
    def _create_promocion_content(self, promocion: Dict) -> str:
        """Create searchable content for promocion"""
        parts = [
            f"Promoción: {promocion['descripcion']}",
            f"Descuento: {promocion['descuentoPorcentaje']}%" if promocion['descuentoPorcentaje'] else "",
            f"Válida desde: {promocion['fechaInicio']}" if promocion['fechaInicio'] else "",
            f"Válida hasta: {promocion['fechaFin']}" if promocion['fechaFin'] else ""
        ]
        
        if promocion.get('productos_nombres'):
            parts.append(f"Productos en promoción: {promocion['productos_nombres']}")
        if promocion.get('productos_detalles'):
            parts.append(f"Detalles de productos: {promocion['productos_detalles']}")
        if promocion.get('total_productos', 0) > 0:
            parts.append(f"Total de productos: {promocion['total_productos']}")
        
        return " | ".join([p for p in parts if p])
    
    async def _sync_productos_incremental(self, since: datetime) -> int:
        """Sync productos modified since timestamp"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                SELECT p.*, c.nombre as categoria_nombre,
                       GROUP_CONCAT(DISTINCT CONCAT(pr.descripcion, ':', pr.descuentoPorcentaje, '%') SEPARATOR ' | ') as promociones_activas
                FROM producto p 
                LEFT JOIN categoria c ON p.categoriaId = c.id
                LEFT JOIN promocionProducto pp ON p.id = pp.productoId
                LEFT JOIN promocion pr ON pp.promocionId = pr.id 
                    AND pr.fechaInicio <= CURDATE() 
                    AND pr.fechaFin >= CURDATE()
                WHERE p.fechaActualizacion >= %s
                GROUP BY p.id, p.nombre, p.descripcion, p.precio, p.stock, p.talla, p.color, p.categoriaId, c.nombre
                """
                cursor.execute(sql, (since,))
                productos = cursor.fetchall()
                
                synced_count = 0
                for producto in productos:
                    content = self._create_producto_content(producto)
                    embedding = await self.embedding_service.generate_embedding(content)
                    
                    doc_id = int(producto['id'])
                    
                    await self.qdrant_service.upsert_document(
                        doc_id=doc_id,
                        content=content,
                        embedding=embedding,
                        metadata={
                            "type": "producto",
                            "id": producto['id'],
                            "nombre": producto['nombre'],
                            "categoria": producto.get('categoria_nombre', ''),
                            "categoria_id": producto['categoriaId'],
                            "precio": float(producto['precio']) if producto['precio'] else 0.0,
                            "disponible": producto['stock'] > 0,
                            "descripcion": producto.get('descripcion', ''),
                            "stock": producto['stock'],
                            "promociones_activas": producto.get('promociones_activas', '') or ''
                        }
                    )
                    synced_count += 1
                
                return synced_count
        finally:
            connection.close()
    
    async def _sync_categorias_incremental(self, since: datetime) -> int:
        """Sync categorias modified since timestamp"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM categoria WHERE fechaActualizacion >= %s"
                cursor.execute(sql, (since,))
                categorias = cursor.fetchall()
                
                synced_count = 0
                for categoria in categorias:
                    content = self._create_categoria_content(categoria)
                    embedding = await self.embedding_service.generate_embedding(content)
                    
                    doc_id = int(categoria['id']) + 1000000
                    
                    await self.qdrant_service.upsert_document(
                        doc_id=doc_id,
                        content=content,
                        embedding=embedding,
                        metadata={
                            "type": "categoria",
                            "id": categoria['id'],
                            "nombre": categoria['nombre'],
                            "descripcion": categoria.get('descripcion', '')
                        }
                    )
                    synced_count += 1
                
                return synced_count
        finally:
            connection.close()

    async def _sync_promociones_incremental(self, since: datetime) -> int:
        """Sync promociones modified since timestamp"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                SELECT pr.*, 
                       GROUP_CONCAT(DISTINCT p.nombre SEPARATOR ', ') as productos_nombres,
                       GROUP_CONCAT(DISTINCT CONCAT(p.nombre, ' ($', p.precio, ')') SEPARATOR ', ') as productos_detalles,
                       COUNT(DISTINCT p.id) as total_productos
                FROM promocion pr
                LEFT JOIN promocionProducto pp ON pr.id = pp.promocionId
                LEFT JOIN producto p ON pp.productoId = p.id
                WHERE pr.fechaInicio <= CURDATE() 
                    AND pr.fechaFin >= CURDATE()
                GROUP BY pr.id
                """
                cursor.execute(sql, (since,))
                promociones = cursor.fetchall()
                
                synced_count = 0
                for promocion in promociones:
                    content = self._create_promocion_content(promocion)
                    embedding = await self.embedding_service.generate_embedding(content)
                    
                    from datetime import date
                    today = date.today()
                    is_active = (promocion['fechaInicio'] <= today <= promocion['fechaFin'])
                    
                    doc_id = int(promocion['id']) + 2000000
                    
                    await self.qdrant_service.upsert_document(
                        doc_id=doc_id,
                        content=content,
                        embedding=embedding,
                        metadata={
                            "type": "promocion",
                            "id": promocion['id'],
                            "descripcion": promocion['descripcion'],
                            "descuento": float(promocion['descuentoPorcentaje']) if promocion['descuentoPorcentaje'] else 0.0,
                            "fecha_inicio": promocion['fechaInicio'].isoformat() if promocion['fechaInicio'] else None,
                            "fecha_fin": promocion['fechaFin'].isoformat() if promocion['fechaFin'] else None,
                            "activa": is_active,
                            "productos_nombres": promocion.get('productos_nombres', '') or '',
                            "productos_detalles": promocion.get('productos_detalles', '') or '',
                            "total_productos": promocion.get('total_productos', 0) or 0
                        }
                    )
                    synced_count += 1
                
                return synced_count
        finally:
            connection.close()

    async def get_sync_status(self) -> Dict:
        """Get current synchronization status"""
        try:
            collection_info = self.qdrant_service.get_collection_info()
            
            return {
                "status": "success",
                "message": "Estado de sincronización obtenido",
                "data": {
                    "collection_exists": bool(collection_info),
                    "total_documents": collection_info.get("points_count", 0) if collection_info else 0,
                    "collection_name": collection_info.get("name", "") if collection_info else "",
                    "last_check": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error obteniendo estado: {str(e)}",
                "data": None
            }
