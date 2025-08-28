from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class SyncRequest(BaseModel):
    """Request model for data synchronization"""
    force_full_sync: bool = Field(
        default=False, 
        description="Force complete resync even if data exists"
    )
    sources: Optional[List[str]] = Field(
        default=None,
        description="Specific data sources to sync (productos, categorias, promociones)"
    )

class SyncResponse(BaseModel):
    """Response model for synchronization operations"""
    status: str = Field(description="Operation status (success, error, warning)")
    message: str = Field(description="Human-readable message")
    synced_count: int = Field(description="Number of documents synchronized")
    errors: List[str] = Field(default=[], description="List of errors if any")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional details about the sync operation"
    )
    timestamp: Optional[str] = Field(
        default=None,
        description="Timestamp of the operation"
    )

class SyncStatusResponse(BaseModel):
    """Response model for sync status queries"""
    status: str = Field(description="Status of the query (success, error)")
    message: str = Field(description="Human-readable message")
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Status data including collection info and statistics"
    )

class ChatMessageRequest(BaseModel):
    """Request model for RAG chat messages"""
    message: str = Field(description="User message to process", min_length=1)
    user_id: Optional[int] = Field(
        default=None,
        description="User ID for conversation persistence"
    )
    context_limit: Optional[int] = Field(
        default=5,
        description="Maximum number of context documents to retrieve"
    )

class ChatMessageResponse(BaseModel):
    """Response model for RAG chat messages"""
    status: str = Field(description="Response status")
    message: str = Field(description="Status message")
    data: Dict[str, Any] = Field(description="Response data including reply and sources")

class DocumentMetadata(BaseModel):
    """Metadata for documents stored in Qdrant"""
    type: str = Field(description="Document type (producto, categoria, promocion)")
    id: int = Field(description="Original database ID")
    nombre: str = Field(description="Document name/title")
    categoria: Optional[str] = Field(default="", description="Category name")
    precio: Optional[float] = Field(default=0.0, description="Price if applicable")
    disponible: Optional[bool] = Field(default=True, description="Availability status")
    descuento: Optional[float] = Field(default=0.0, description="Discount percentage")
    activa: Optional[bool] = Field(default=True, description="Active status")

class VectorDocument(BaseModel):
    """Model for vector documents in Qdrant"""
    doc_id: str = Field(description="Unique document identifier")
    content: str = Field(description="Searchable text content")
    embedding: List[float] = Field(description="Vector embedding")
    metadata: DocumentMetadata = Field(description="Document metadata")
    relevance_score: Optional[float] = Field(
        default=0.0,
        description="Relevance score for search results"
    )

class ValidationResult(BaseModel):
    """Model for data validation results"""
    validation_passed: bool = Field(description="Whether validation passed")
    mysql_count: Optional[int] = Field(default=0, description="Count in MySQL")
    qdrant_count: Optional[int] = Field(default=0, description="Count in Qdrant")
    discrepancies: List[str] = Field(default=[], description="Found discrepancies")
    last_validation: str = Field(description="Timestamp of validation")

class CollectionInfo(BaseModel):
    """Model for Qdrant collection information"""
    collection_exists: bool = Field(description="Whether collection exists")
    total_documents: int = Field(description="Total number of documents")
    vector_size: Optional[int] = Field(default=None, description="Vector dimension size")
    distance_metric: Optional[str] = Field(default=None, description="Distance metric used")
    last_updated: Optional[str] = Field(default=None, description="Last update timestamp")
