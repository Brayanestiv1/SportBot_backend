from sentence_transformers import SentenceTransformer
from typing import List, Union
import logging
import numpy as np
from app.config import Config

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        """Initialize embedding model"""
        try:
            self.model = SentenceTransformer(Config.EMBEDDING_MODEL)
            self.dimension = Config.EMBEDDING_DIMENSION
            logger.info(f"Loaded embedding model: {Config.EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            raise

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generates an embedding for a given text using a pre-trained model.
        """
        # Encode the text to a numerical vector
        embedding = self.model.encode(text)
        
        # Convert the numpy array to a list of floats
        return embedding.tolist()
    
    def encode_text(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Encode text into embeddings
        
        Args:
            text: Single text string or list of text strings
            
        Returns:
            Single embedding vector or list of embedding vectors
        """
        try:
            if isinstance(text, str):
                # Single text
                embedding = self.model.encode(text, convert_to_tensor=False)
                return embedding.tolist()
            else:
                # List of texts
                embeddings = self.model.encode(text, convert_to_tensor=False)
                return [emb.tolist() for emb in embeddings]
                
        except Exception as e:
            logger.error(f"Error encoding text: {str(e)}")
            if isinstance(text, str):
                return [0.0] * self.dimension
            else:
                return [[0.0] * self.dimension] * len(text)
    
    def encode_query(self, query: str) -> List[float]:
        """
        Encode a search query into embedding
        
        Args:
            query: Search query string
            
        Returns:
            Embedding vector for the query
        """
        return self.encode_text(query)
    
    def encode_documents(self, documents: List[str]) -> List[List[float]]:
        """
        Encode multiple documents into embeddings
        
        Args:
            documents: List of document texts
            
        Returns:
            List of embedding vectors
        """
        return self.encode_text(documents)
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score between -1 and 1
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def get_model_info(self) -> dict:
        """
        Get information about the loaded model
        
        Returns:
            Dictionary with model information
        """
        return {
            'model_name': Config.EMBEDDING_MODEL,
            'dimension': self.dimension,
            'max_seq_length': getattr(self.model, 'max_seq_length', 'Unknown')
        }
