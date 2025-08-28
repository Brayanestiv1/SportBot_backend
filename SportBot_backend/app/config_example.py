"""
Ejemplo de uso de la configuración unificada de SportBot Assistant
Este archivo muestra cómo usar la configuración para Docker y nuevas funcionalidades
"""

from app.config import settings, Config

def ejemplo_uso_configuracion():
    """Ejemplo de cómo usar la configuración unificada"""
    
    print("=== CONFIGURACIÓN UNIFICADA SPORTBOT ASSISTANT ===\n")
    
    # ===== CONFIGURACIÓN DE DOCKER (Rama Docker) =====
    print("🔧 CONFIGURACIÓN DOCKER:")
    print(f"   - Entorno Docker: {settings.is_docker_environment()}")
    print(f"   - URL Base de datos: {settings.get_database_url()}")
    print(f"   - Configuración Qdrant: {settings.get_qdrant_config()}")
    print(f"   - Configuración Redis: {settings.get_redis_config()}")
    print()
    
    # ===== CONFIGURACIÓN DE TELEGRAM (Rama Telegram) =====
    print("🤖 CONFIGURACIÓN TELEGRAM:")
    telegram_config = settings.get_telegram_config()
    print(f"   - Bot Token configurado: {'✅' if telegram_config['bot_token'] else '❌'}")
    print(f"   - Webhook URL: {telegram_config['webhook_url']}")
    print(f"   - Nombre del Bot: {telegram_config['bot_name']}")
    print()
    
    # ===== CONFIGURACIÓN DE OPENAI/LLM (Rama Telegram) =====
    print("🧠 CONFIGURACIÓN OPENAI/LLM:")
    openai_config = settings.get_openai_config()
    print(f"   - API Key configurada: {'✅' if openai_config['api_key'] else '❌'}")
    print(f"   - Modelo: {openai_config['model']}")
    print(f"   - Modelo de Embeddings: {settings.EMBEDDING_MODEL}")
    print(f"   - Dimensión de Embeddings: {settings.EMBEDDING_DIMENSION}")
    print()
    
    # ===== VALIDACIÓN DE CONFIGURACIÓN =====
    print("✅ VALIDACIÓN:")
    try:
        settings.validate_required()
        print("   - Configuración válida")
    except ValueError as e:
        print(f"   - Errores de configuración: {e}")
    print()
    
    # ===== COMPATIBILIDAD CON CÓDIGO EXISTENTE =====
    print("🔄 COMPATIBILIDAD:")
    print("   - settings.APP_NAME:", settings.APP_NAME)
    print("   - Config.APP_NAME:", Config.APP_NAME)  # Alias para compatibilidad
    print("   - settings.DEBUG:", settings.DEBUG)
    print("   - Config.DEBUG:", Config.DEBUG)  # Alias para compatibilidad

def ejemplo_uso_telegram():
    """Ejemplo de cómo usar la configuración para Telegram"""
    print("=== EJEMPLO USO TELEGRAM ===")
    
    # Obtener configuración de Telegram
    telegram_config = settings.get_telegram_config()
    
    if telegram_config['bot_token']:
        print(f"✅ Bot configurado: {telegram_config['bot_name']}")
        print(f"   Token: {telegram_config['bot_token'][:10]}...")
        print(f"   Webhook: {telegram_config['webhook_url']}")
    else:
        print("❌ Bot de Telegram no configurado")
        print("   Configura TELEGRAM_BOT_TOKEN en tu archivo .env")

def ejemplo_uso_openai():
    """Ejemplo de cómo usar la configuración para OpenAI"""
    print("=== EJEMPLO USO OPENAI ===")
    
    # Obtener configuración de OpenAI
    openai_config = settings.get_openai_config()
    
    if openai_config['api_key']:
        print(f"✅ OpenAI configurado")
        print(f"   Modelo: {openai_config['model']}")
        print(f"   API Key: {openai_config['api_key'][:10]}...")
        print(f"   Embeddings: {settings.EMBEDDING_MODEL}")
    else:
        print("❌ OpenAI no configurado")
        print("   Configura OPENAI_API_KEY en tu archivo .env")

def ejemplo_uso_docker():
    """Ejemplo de cómo usar la configuración para Docker"""
    print("=== EJEMPLO USO DOCKER ===")
    
    if settings.is_docker_environment():
        print("✅ Ejecutando en entorno Docker")
        print(f"   Base de datos: {settings.get_database_url()}")
        print(f"   Qdrant: {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
        print(f"   Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    else:
        print("🖥️ Ejecutando en entorno local")
        print(f"   Base de datos: {settings.get_database_url()}")
        print(f"   Qdrant: {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
        print(f"   Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")

if __name__ == "__main__":
    ejemplo_uso_configuracion()
    print("\n" + "="*50 + "\n")
    ejemplo_uso_telegram()
    print("\n" + "="*50 + "\n")
    ejemplo_uso_openai()
    print("\n" + "="*50 + "\n")
    ejemplo_uso_docker()
