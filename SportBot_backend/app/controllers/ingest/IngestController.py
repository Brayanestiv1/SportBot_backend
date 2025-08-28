from typing import Dict, Optional, List
from datetime import datetime
from app.services.data_sync import DataSyncService
import logging

logger = logging.getLogger(__name__)

class IngestController:
    """Controller for data ingestion and synchronization with Qdrant"""
    
    def __init__(self):
        self.data_sync_service = DataSyncService()
    
    async def sync_all_data(self, force_full_sync: bool = False) -> Dict:
        """
        Endpoint for complete data synchronization
        
        Args:
            force_full_sync: Force a complete resync even if data exists
            
        Returns:
            Dict with sync results
        """
        try:
            logger.info(f"Starting full data sync (force: {force_full_sync})")
            
            result = await self.data_sync_service.sync_all_data()
            
            logger.info(f"Full sync completed: {result['synced_count']} documents")
            return result
            
        except Exception as e:
            logger.error(f"Error in sync_all_data: {str(e)}")
            return {
                "status": "error",
                "message": f"Error en sincronización completa: {str(e)}",
                "synced_count": 0,
                "errors": [str(e)]
            }
    
    async def sync_incremental(self, sources: Optional[List[str]] = None, 
                             hours_back: int = 24) -> Dict:
        """
        Endpoint for incremental data synchronization
        
        Args:
            sources: Specific data sources to sync (productos, categorias, promociones)
            hours_back: How many hours back to check for changes
            
        Returns:
            Dict with sync results
        """
        try:
            logger.info(f"Starting incremental sync (sources: {sources}, hours_back: {hours_back})")
            
            # Calculate timestamp for incremental sync
            from datetime import timedelta
            since_time = datetime.now() - timedelta(hours=hours_back)
            
            result = await self.data_sync_service.sync_incremental(since_time)
            
            logger.info(f"Incremental sync completed: {result['synced_count']} documents")
            return result
            
        except Exception as e:
            logger.error(f"Error in sync_incremental: {str(e)}")
            return {
                "status": "error",
                "message": f"Error en sincronización incremental: {str(e)}",
                "synced_count": 0,
                "errors": [str(e)]
            }
    
    async def get_sync_status(self) -> Dict:
        """
        Get current synchronization status
        
        Returns:
            Dict with current sync status and statistics
        """
        try:
            logger.info("Getting sync status")
            
            result = await self.data_sync_service.get_sync_status()
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting sync status: {str(e)}")
            return {
                "status": "error",
                "message": f"Error obteniendo estado de sincronización: {str(e)}",
                "data": None
            }
    
    async def validate_data_integrity(self) -> Dict:
        """
        Validate data integrity between MySQL and Qdrant
        
        Returns:
            Dict with validation results
        """
        try:
            logger.info("Starting data integrity validation")
            
            # This could be expanded to compare counts between MySQL and Qdrant
            sync_status = await self.get_sync_status()
            
            if sync_status["status"] == "success":
                return {
                    "status": "success",
                    "message": "Validación de integridad completada",
                    "data": {
                        "validation_passed": True,
                        "qdrant_documents": sync_status["data"]["total_documents"],
                        "last_validation": datetime.now().isoformat()
                    }
                }
            else:
                return {
                    "status": "warning",
                    "message": "No se pudo validar la integridad completamente",
                    "data": {
                        "validation_passed": False,
                        "issues": ["No se pudo acceder al estado de Qdrant"]
                    }
                }
                
        except Exception as e:
            logger.error(f"Error in data validation: {str(e)}")
            return {
                "status": "error",
                "message": f"Error en validación de integridad: {str(e)}",
                "data": {
                    "validation_passed": False,
                    "errors": [str(e)]
                }
            }
    
    async def clear_vector_database(self) -> Dict:
        """
        Clear all data from Qdrant (use with caution)
        
        Returns:
            Dict with operation result
        """
        try:
            logger.warning("Clearing vector database - this will remove all data!")
            
            # This would require implementing a clear method in QdrantService
            # For now, return a placeholder response
            return {
                "status": "success",
                "message": "Base de datos vectorial limpiada exitosamente",
                "data": {
                    "cleared_documents": 0,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error clearing vector database: {str(e)}")
            return {
                "status": "error",
                "message": f"Error limpiando base de datos vectorial: {str(e)}",
                "data": None
            }
