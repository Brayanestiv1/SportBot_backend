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
                SELECT p.*, c.nombre as categoria_nombre 
                FROM producto p 
                LEFT JOIN categoria c ON p.categoriaId = c.id
                """
                cursor.execute(sql)
                productos = cursor.fetchall()
                
                synced_count = 0
                for producto in productos:
                    # Create searchable text content
                    content = self._create_producto_content(producto)
                    
                    # Generate embedding
                    embedding = await self.embedding_service.generate_embedding(content)
                    
                    # Store in Qdrant
                    await self.qdrant_service.upsert_document(
                        doc_id=f"producto_{producto['id']}",
                        content=content,
                        embedding=embedding,
                        metadata={
                            "type": "producto",
                            "id": producto['id'],
                            "nombre": producto['nombre'],
                            "categoria": producto.get('categoria_nombre', ''),
                            "precio": float(producto['precio']) if producto['precio'] else 0.0,
                            "disponible": bool(producto['disponible'])
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
                    
                    await self.qdrant_service.upsert_document(
                        doc_id=f"categoria_{categoria['id']}",
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
        """Sync all promociones to Qdrant"""
        connection = get_sync_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                SELECT p.*, pr.nombre as producto_nombre 
                FROM promocion p 
                LEFT JOIN producto pr ON p.productoId = pr.id
                """
                cursor.execute(sql)
                promociones = cursor.fetchall()
                
                synced_count = 0
                for promocion in promociones:
                    content = self._create_promocion_content(promocion)
                    embedding = await self.embedding_service.generate_embedding(content)
                    
                    await self.qdrant_service.upsert_document(
                        doc_id=f"promocion_{promocion['id']}",
                        content=content,
                        embedding=embedding,
                        metadata={
                            "type": "promocion",
                            "id": promocion['id'],
                            "titulo": promocion['titulo'],
                            "descuento": float(promocion['descuento']) if promocion['descuento'] else 0.0,
                            "producto": promocion.get('producto_nombre', ''),
                            "activa": bool(promocion['activa'])
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
            f"Descripción: {producto.get('descripcion', '')}",
            f"Categoría: {producto.get('categoria_nombre', '')}",
            f"Precio: ${producto['precio']}" if producto['precio'] else "",
            f"Disponible: {'Sí' if producto['disponible'] else 'No'}"
        ]
        return " | ".join([p for p in parts if p])
    
    def _create_categoria_content(self, categoria: Dict) -> str:
        """Create searchable content for categoria"""
        parts = [
            f"Categoría: {categoria['nombre']}",
            f"Descripción: {categoria.get('descripcion', '')}"
        ]
        return " | ".join([p for p in parts if p])
    
    def _create_promocion_content(self, promocion: Dict) -> str:
        """Create searchable content for promocion"""
        parts = [
            f"Promoción: {promocion['titulo']}",
            f"Descripción: {promocion.get('descripcion', '')}",
            f"Descuento: {promocion['descuento']}%" if promocion['descuento'] else "",
            f"Producto: {promocion.get('producto_nombre', '')}",
            f"Estado: {'Activa' if promocion['activa'] else 'Inactiva'}"
        ]
        return " | ".join([p for p in parts if p])
    
    async def _sync_productos_incremental(self, since: datetime) -> int:
        """Sync productos modified since timestamp"""
        # Implementation for incremental sync
        # This would require modification timestamps in the database
        return await self._sync_productos()  # Fallback to full sync for now
    
    async def _sync_categorias_incremental(self, since: datetime) -> int:
        """Sync categorias modified since timestamp"""
        return await self._sync_categorias()  # Fallback to full sync for now
    
    async def _sync_promociones_incremental(self, since: datetime) -> int:
        """Sync promociones modified since timestamp"""
        return await self._sync_promociones()  # Fallback to full sync for now
    
    async def get_sync_status(self) -> Dict:
        """Get current synchronization status"""
        try:
            collection_info = self.qdrant_service.get_collection_info()
            
            return {
                "status": "success",
                "message": "Estado de sincronización obtenido",
                "data": {
                    "collection_exists": collection_info is not None,
                    "total_documents": collection_info.get("vectors_count", 0) if collection_info else 0,
                    "last_check": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error obteniendo estado: {str(e)}",
                "data": None
            }
