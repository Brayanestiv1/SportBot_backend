from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from app.controllers.ingest.IngestController import IngestController
from app.models.ingest.IngestModel import SyncRequest, SyncResponse, SyncStatusResponse

router = APIRouter(prefix="/ingest", tags=["ingest"])

# Initialize controller
ingest_controller = IngestController()

@router.post("/sync-all", response_model=SyncResponse)
async def sync_all_data(request: SyncRequest):
    """
    Perform complete data synchronization from MySQL to Qdrant
    
    - **force_full_sync**: Force complete resync even if data exists
    - **sources**: Specific data sources to sync (optional)
    """
    try:
        result = await ingest_controller.sync_all_data(
            force_full_sync=request.force_full_sync
        )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
        
        return SyncResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en sincronización completa: {str(e)}"
        )

@router.post("/sync-incremental", response_model=SyncResponse)
async def sync_incremental(
    sources: Optional[List[str]] = Query(None, description="Specific sources to sync"),
    hours_back: int = Query(24, description="Hours back to check for changes")
):
    """
    Perform incremental data synchronization
    
    - **sources**: Specific data sources to sync (productos, categorias, promociones)
    - **hours_back**: How many hours back to check for changes (default: 24)
    """
    try:
        result = await ingest_controller.sync_incremental(
            sources=sources,
            hours_back=hours_back
        )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
        
        return SyncResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en sincronización incremental: {str(e)}"
        )

@router.get("/status", response_model=SyncStatusResponse)
async def get_sync_status():
    """
    Get current synchronization status and statistics
    """
    try:
        result = await ingest_controller.get_sync_status()
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
        
        return SyncStatusResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estado: {str(e)}"
        )

@router.post("/validate", response_model=SyncStatusResponse)
async def validate_data_integrity():
    """
    Validate data integrity between MySQL and Qdrant
    """
    try:
        result = await ingest_controller.validate_data_integrity()
        
        return SyncStatusResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en validación: {str(e)}"
        )

@router.delete("/clear", response_model=SyncStatusResponse)
async def clear_vector_database():
    """
    Clear all data from Qdrant vector database
    
    ⚠️ **WARNING**: This will permanently delete all vectorized data!
    """
    try:
        result = await ingest_controller.clear_vector_database()
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
        
        return SyncStatusResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error limpiando base de datos: {str(e)}"
        )
