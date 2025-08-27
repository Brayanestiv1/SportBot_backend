import logging
from typing import Dict, Any, Optional, List
from openai import AsyncOpenAI
from app.config import Config
from app.services.qdrant import QdrantService
from app.services.embedding import EmbeddingService

logger = logging.getLogger(__name__)

# ==============================
# Agente RAG Principal
# ==============================

class AgentService:
    def __init__(self):
        self.qdrant_service = QdrantService()
        self.embedding_service = EmbeddingService()
        
        if Config.OPENAI_API_KEY:
            try:
                self.openai_client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
                logger.info("✅ Cliente OpenAI inicializado para AgentService")
            except Exception as e:
                logger.error(f"Error inicializando OpenAI: {e}")
                self.openai_client = None
        else:
            logger.warning("⚠️ No se encontró OPENAI_API_KEY")
            self.openai_client = None

    async def process_query(self, query: str, user_id: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Procesa una consulta del usuario usando RAG (Qdrant + embeddings)
        """
        try:
            logger.info(f"Processing query: {query[:50]}...")
            
            query_embedding = await self.embedding_service.generate_embedding(query)
            logger.debug(f"Generated embedding with dimension: {len(query_embedding)}")

            relevant_docs = self.qdrant_service.search_similar(
                query_embedding,
                limit=5
            )
            
            if not relevant_docs:
                logger.warning("No relevant documents found in Qdrant - database may be empty")
                return {
                    "reply": "Lo siento, parece que la base de datos de productos no está disponible en este momento. Por favor, contacta al administrador para sincronizar los datos.",
                    "sources": [],
                    "relevance_score": 0.0,
                    "context_used": [],
                    "error": "empty_database"
                }
            
            logger.info(f"Found {len(relevant_docs)} relevant documents")
            context_text = self._build_context(relevant_docs, context)

            response_text = await self._generate_response(query, context_text, user_id)

            return {
                "reply": response_text,
                "sources": [doc.get("payload", {}).get("nombre", "Unknown") for doc in relevant_docs],
                "relevance_score": relevant_docs[0].get("score", 0.0) if relevant_docs else 0.0,
                "context_used": [doc.get("payload", {}) for doc in relevant_docs]
            }

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "reply": "Lo siento, hubo un error procesando tu consulta. Por favor intenta de nuevo o contacta al administrador si el problema persiste.",
                "sources": [],
                "relevance_score": 0.0,
                "context_used": [],
                "error": str(e)
            }

    def _build_context(self, relevant_docs: List[Dict], additional_context: Optional[Dict] = None) -> str:
        """
        Construye el contexto a partir de documentos relevantes de la KB
        """
        context_parts = []

        if relevant_docs:
            context_parts.append("📦 Información de productos disponibles:")
            for doc in relevant_docs:
                payload = doc.get("payload", {})
                
                nombre = payload.get('nombre', 'N/A')
                descripcion = payload.get('descripcion', 'N/A')
                precio = payload.get('precio', 'N/A')
                categoria = payload.get('categoria', 'N/A')
                
                context_parts.append(f"- **{nombre}**")
                context_parts.append(f"  📝 Descripción: {descripcion}")
                context_parts.append(f"  💰 Precio: ${precio}")
                context_parts.append(f"  📂 Categoría: {categoria}")
                context_parts.append("")

        if additional_context:
            context_parts.append("ℹ️ Información adicional:")
            for key, value in additional_context.items():
                context_parts.append(f"- {key}: {value}")

        return "\n".join(context_parts) if context_parts else "No se encontró información específica en la base de datos."

    async def _generate_response(self, query: str, context: str, user_id: str) -> str:
        """
        Genera respuesta usando OpenAI con el contexto de la KB real
        """
        system_prompt = """
        Eres BaekhoBot 🥋, asistente comercial especializado en productos de Taekwondo y artes marciales.
        
        INSTRUCCIONES IMPORTANTES:
        - SOLO usa información del contexto proporcionado (datos reales de la base de datos)
        - Si no tienes información específica, dilo claramente
        - NO inventes precios, productos o características
        - Sé amigable, profesional y conciso
        - Incluye emojis relevantes para hacer la conversación más amena
        - Si el contexto está vacío, explica que necesitas más información o que no tienes datos sobre esa consulta específica
        
        Tu objetivo es ayudar a los clientes con información REAL y precisa sobre nuestros productos.
        """

        user_prompt = f"""
        Consulta del cliente: {query}

        Información disponible en nuestra base de datos:
        {context}
        
        Por favor responde basándote ÚNICAMENTE en la información proporcionada arriba.
        """

        try:
            if not self.openai_client:
                return "Lo siento, el servicio de chat inteligente no está disponible en este momento. Verifica que la API key de OpenAI esté configurada correctamente."

            logger.debug("Sending request to OpenAI...")
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=600,
                temperature=0.3  # Lower temperature for more consistent responses
            )

            generated_response = response.choices[0].message.content.strip()
            logger.debug(f"OpenAI response generated successfully: {len(generated_response)} characters")
            return generated_response

        except Exception as e:
            logger.error(f"Error generating response with OpenAI: {str(e)}")
            return "Lo siento, hubo un error generando la respuesta. Por favor intenta de nuevo o verifica la configuración de OpenAI."

# ==============================
# Agente Principal (Orquestador)
# ==============================

class BaekhoAgent:
    """
    Agente principal que usa únicamente la knowledge base real de Qdrant
    """
    def __init__(self):
        self.rag_agent = AgentService()

    async def process_message(self, message: str, user_info: Dict[str, Any] = None) -> str:
        """
        Procesa mensajes usando únicamente la knowledge base real
        """
        try:
            user_id = user_info.get("id", "anonimo") if user_info else "anonimo"
            response_dict = await self.rag_agent.process_query(message, user_id)
            response = response_dict.get("reply", "")
            
            if not response:
                return "Lo siento, no pude procesar tu consulta en este momento. Por favor intenta de nuevo."
                
            return response
            
        except Exception as e:
            logger.error(f"Error in BaekhoAgent.process_message: {str(e)}")
            return "Hubo un error procesando tu mensaje. Por favor intenta de nuevo."

    def get_model_info(self) -> Dict[str, Any]:
        """
        Información del modelo actual
        """
        return {
            "model": "BaekhoBot RAG",
            "version": "2.0",
            "knowledge_source": "MySQL + Qdrant Vector DB",
            "description": "Asistente comercial con información real de productos"
        }

    def is_available(self) -> bool:
        """
        Verifica si el agente está disponible
        """
        return self.rag_agent.openai_client is not None
