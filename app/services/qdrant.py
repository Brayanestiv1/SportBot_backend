# Si se requiere recuperar contexto desde la base vectorial antes de enviar al LLM

import os
import logging
import uuid
from typing import List, Dict, Any, Optional

from qdrant_client import QdrantClient
from qdrant_client import models
from qdrant_client.models import Filter, FieldCondition, MatchValue, SearchRequest, PointStruct, VectorParams, Distance
from app.config import *

logger = logging.getLogger(__name__)

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = os.getenv("QDRANT_PORT", 6333)
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "sportbot_collection")
QDRANT_ENABLED = os.getenv("QDRANT_ENABLED", "true").lower() == "true"

# Embeddings: puedes cambiar por OpenAI con una flag (ver requisitos). :contentReference[oaicite:2]{index=2}
EMBED_MODEL = os.getenv("EMBED_MODEL", "intfloat/multilingual-e5-small")
VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", 384))

_client: Optional[QdrantClient] = None

class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            host=QDRANT_HOST,
            port=QDRANT_PORT,
            api_key=QDRANT_API_KEY if QDRANT_API_KEY else None
        )
        self.collection_name = QDRANT_COLLECTION_NAME
        self.vector_size = VECTOR_SIZE

    def create_collection_if_not_exists(self):
        """Create collection if it doesn't exist"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            raise
        
    def initialize_collection(self):
        """Create collection if it doesn't exist"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                
        except Exception as e:
            logger.error(f"Error initializing collection: {str(e)}")
            raise
    
    async def upsert_document(self, doc_id: str, content: str, embedding: List[float], 
                            metadata: Dict[str, Any]) -> bool:
        """Insert or update a single document in Qdrant"""
        try:
            point = PointStruct(
                id=doc_id,
                vector=embedding,
                payload={
                    'content': content,
                    'metadata': metadata,
                    'tipo': metadata.get('type', 'producto'),
                    'categoria_id': metadata.get('categoria_id'),
                    'precio': metadata.get('precio'),
                    'disponible': metadata.get('disponible', True),
                    'nombre': metadata.get('nombre', ''),
                    'categoria': metadata.get('categoria', ''),
                    'descripcion': metadata.get('descripcion', ''),
                    'descuento': metadata.get('descuento', 0.0),
                    'activa': metadata.get('activa', True)
                }
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.debug(f"Upserted document {doc_id} to Qdrant")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting document {doc_id}: {str(e)}")
            return False
    
    def upsert_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Insert or update documents in Qdrant"""
        try:
            points = []
            for doc in documents:
                point = PointStruct(
                    id=str(uuid.uuid4()) if 'id' not in doc else str(doc['id']),
                    vector=doc['vector'],
                    payload={
                        'content': doc.get('content', ''),
                        'metadata': doc.get('metadata', {}),
                        'tipo': doc.get('tipo', 'producto'),
                        'categoria_id': doc.get('categoria_id'),
                        'precio': doc.get('precio'),
                        'disponible': doc.get('disponible', True)
                    }
                )
                points.append(point)
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Upserted {len(points)} documents to Qdrant")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting documents: {str(e)}")
            return False
    
    def search_similar(self, query_vector: List[float], limit: int = 5, 
                      filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            try:
                collection_info = self.client.get_collection(self.collection_name)
                if collection_info.points_count == 0:
                    logger.warning(f"Collection {self.collection_name} exists but is empty")
                    return []
            except Exception as e:
                logger.error(f"Collection {self.collection_name} not found or inaccessible: {str(e)}")
                return []
            
            search_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    if isinstance(value, list):
                        conditions.append(
                            models.FieldCondition(
                                key=key,
                                match=models.MatchAny(any=value)
                            )
                        )
                    else:
                        conditions.append(
                            models.FieldCondition(
                                key=key,
                                match=models.MatchValue(value=value)
                            )
                        )
                
                if conditions:
                    search_filter = models.Filter(must=conditions)
            
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=search_filter,
                with_payload=True
            )
            
            documents = []
            for result in results:
                doc = {
                    'id': result.id,
                    'score': result.score,
                    'content': result.payload.get('content', ''),
                    'payload': result.payload,  # Incluir payload completo
                    'metadata': result.payload.get('metadata', {}),
                    'tipo': result.payload.get('tipo', 'producto'),
                    'categoria_id': result.payload.get('categoria_id'),
                    'precio': result.payload.get('precio'),
                    'disponible': result.payload.get('disponible', True)
                }
                documents.append(doc)
            
            logger.debug(f"Found {len(documents)} similar documents with scores: {[d['score'] for d in documents]}")
            return documents
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []

    def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents by IDs"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=document_ids
                )
            )
            
            logger.info(f"Deleted {len(document_ids)} documents from Qdrant")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information"""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                'name': self.collection_name,
                'vectors_count': info.vectors_count if hasattr(info, 'vectors_count') else 0,
                'points_count': info.points_count,
                'status': info.status
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {}
    
    def clear_collection(self) -> bool:
        """Clear all documents from collection"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must_not=[
                            models.HasIdCondition(has_id=["non_existent_id"])
                        ]
                    )
                )
            )
            logger.info(f"Cleared collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            return False
