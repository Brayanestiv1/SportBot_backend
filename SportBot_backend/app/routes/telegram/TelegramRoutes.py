# Definir la ruta que recibe los webhooks de Telegram.

from fastapi import APIRouter, HTTPException, Depends
from app.models.telegram.TelegramModel import TelegramWebhookRequest
from app.controllers.telegram.TelegramController import TelegramController
import logging

# Configurar logger
logger = logging.getLogger(__name__)

# Crear router
telegram_router = APIRouter(prefix="/telegram", tags=["telegram"])

# Instancia del controlador
telegram_controller = TelegramController()


@telegram_router.post("/webhook")
async def telegram_webhook(webhook_data: TelegramWebhookRequest):
    
    # Endpoint que recibe los webhooks de Telegram
    
    try:
        logger.info(f"Webhook recibido: {webhook_data.dict()}")
        
        # Procesar el mensaje a través del controlador
        await telegram_controller.process_message(webhook_data)
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error procesando webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@telegram_router.get("/health")
async def health_check():
    
    # Endpoint de health check para verificar que el servicio está funcionando
    
    return {"status": "healthy", "service": "telegram_bot"}