from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from app.controllers.chat.ChatController import ChatController
from app.controllers.mensaje.MensajeController import MensajeController
from app.models.chat.ChatModel import ChatCreate, ChatUpdate, ChatResponse
from app.models.mensaje.MensajeModel import MensajeCreate, MensajeUpdate, MensajeResponse
from app.models.ingest.IngestModel import ChatMessageRequest, ChatMessageResponse

# Separate routers for different access levels
admin_router = APIRouter(prefix="/admin/chats", tags=["admin-chats"])
router = APIRouter(prefix="/chats", tags=["chats"])
messages_router = APIRouter(prefix="/messages", tags=["messages"])

# Initialize controllers
chat_controller = ChatController()
mensaje_controller = MensajeController()

# ========== PUBLIC CHAT ENDPOINTS ==========

@router.post("/message", response_model=ChatMessageResponse)
async def process_message(request: ChatMessageRequest):
    """
    Process user message using RAG (Retrieval-Augmented Generation)
    
    This endpoint uses vector search to find relevant context and generates
    intelligent responses about products, categories, and promotions.
    Automatically persists the conversation if user_id is provided.
    """
    try:
        result = await chat_controller.process_message(
            message=request.message,
            user_id=request.user_id
        )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
        
        return ChatMessageResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando mensaje: {str(e)}"
        )

@router.get("/{chat_id}/history", response_model=List[MensajeResponse])
def get_chat_history(
    chat_id: int,
    limit: int = Query(50, ge=1, le=500, description="Number of messages to retrieve"),
    offset: int = Query(0, ge=0, description="Number of messages to skip")
):
    """Get chat message history with pagination"""
    try:
        # Verify chat exists
        chat = ChatController.get_chat_by_id(chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Chat not found"
            )
        
        messages = MensajeController.get_mensajes_by_chat(chat_id, limit, offset)
        return messages
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo historial: {str(e)}"
        )

@router.get("/{chat_id}/recent", response_model=List[MensajeResponse])
def get_recent_messages(
    chat_id: int,
    minutes: int = Query(60, ge=1, le=1440, description="Minutes back to retrieve messages")
):
    """Get recent messages from a chat within specified time frame"""
    try:
        # Verify chat exists
        chat = ChatController.get_chat_by_id(chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Chat not found"
            )
        
        messages = MensajeController.get_recent_mensajes_by_chat(chat_id, minutes)
        return messages
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo mensajes recientes: {str(e)}"
        )

@router.get("/usuario/{usuario_id}", response_model=List[ChatResponse])
def get_user_chats(usuario_id: int):
    """Get all chats for a specific user"""
    return ChatController.get_chats_by_usuario(usuario_id)

# ========== CHAT CRUD ENDPOINTS ==========

@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
def create_chat(chat: ChatCreate):
    """Create a new chat"""
    try:
        return ChatController.create_chat(chat)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{chat_id}", response_model=ChatResponse)
def get_chat(chat_id: int):
    """Get chat by ID"""
    chat = ChatController.get_chat_by_id(chat_id)
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return chat

@router.put("/{chat_id}", response_model=ChatResponse)
def update_chat(chat_id: int, chat: ChatUpdate):
    """Update chat"""
    updated_chat = ChatController.update_chat(chat_id, chat)
    if not updated_chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return updated_chat

@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(chat_id: int):
    """Delete chat and all its messages"""
    if not ChatController.delete_chat(chat_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

# ========== ADMIN ENDPOINTS ==========

@admin_router.get("/", response_model=List[ChatResponse])
def get_all_chats():
    """Get all chats (Admin only)"""
    return ChatController.get_all_chats()

@admin_router.get("/{chat_id}/summary")
def get_chat_summary(
    chat_id: int,
    last_messages: int = Query(10, ge=1, le=50, description="Number of recent messages for summary")
):
    """Get chat conversation summary (Admin only)"""
    try:
        # Verify chat exists
        chat = ChatController.get_chat_by_id(chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Chat not found"
            )
        
        summary = MensajeController.get_chat_conversation_summary(chat_id, last_messages)
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo resumen: {str(e)}"
        )

@admin_router.get("/{chat_id}/statistics")
def get_chat_statistics(chat_id: int):
    """Get chat statistics (Admin only)"""
    try:
        # Verify chat exists
        chat = ChatController.get_chat_by_id(chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Chat not found"
            )
        
        stats = MensajeController.get_chat_statistics(chat_id)
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )

# ========== MESSAGE ENDPOINTS ==========

@messages_router.post("/", response_model=MensajeResponse, status_code=status.HTTP_201_CREATED)
def create_message(mensaje: MensajeCreate):
    """Create a new message"""
    try:
        return MensajeController.create_mensaje(mensaje)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@messages_router.get("/{mensaje_id}", response_model=MensajeResponse)
def get_message(mensaje_id: int):
    """Get message by ID"""
    mensaje = MensajeController.get_mensaje_by_id(mensaje_id)
    if not mensaje:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    return mensaje

@messages_router.put("/{mensaje_id}", response_model=MensajeResponse)
def update_message(mensaje_id: int, mensaje: MensajeUpdate):
    """Update message content"""
    updated_mensaje = MensajeController.update_mensaje(mensaje_id, mensaje)
    if not updated_mensaje:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    return updated_mensaje

@messages_router.delete("/{mensaje_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(mensaje_id: int):
    """Delete message"""
    if not MensajeController.delete_mensaje(mensaje_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

@messages_router.get("/", response_model=List[MensajeResponse])
def get_all_messages(
    limit: int = Query(100, ge=1, le=1000, description="Number of messages to retrieve"),
    offset: int = Query(0, ge=0, description="Number of messages to skip")
):
    """Get all messages with pagination (Admin use)"""
    return MensajeController.get_all_mensajes()[offset:offset+limit]