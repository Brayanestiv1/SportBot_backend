import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Configuración unificada para SportBot Assistant - Compatible con Docker y nuevas funcionalidades"""
    
    # ===== CONFIGURACIÓN DE LA APLICACIÓN =====
    APP_NAME: str = "SportBot Assistant"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # ===== CONFIGURACIÓN DEL SERVIDOR =====
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # ===== CONFIGURACIÓN DE BASE DE DATOS =====
    # Configuración para Docker (por defecto)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql://root:admin@db:3306/sportbot_db")
    
    # Configuración alternativa para desarrollo local (compatible con ambas ramas)
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3307"))  # Puerto cambiado para evitar conflictos
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "admin")
    DB_NAME: str = os.getenv("DB_NAME", "sportbot_db")
    DB_SSL_CA: str = os.getenv("CA_PATH", "")
    
    # ===== CONFIGURACIÓN DE QDRANT =====
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "sportbot_collection")
    
    # ===== CONFIGURACIÓN DE REDIS =====
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    
    # ===== CONFIGURACIÓN DE OPENAI/LLM =====
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # ===== CONFIGURACIÓN DE EMBEDDINGS =====
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))
    
    # ===== CONFIGURACIÓN DE TELEGRAM =====
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_WEBHOOK_URL: str = os.getenv("TELEGRAM_WEBHOOK_URL", "")
    BOT_NAME: str = os.getenv("BOT_NAME", "SportBot")
    
    # ===== CONFIGURACIÓN DE SEGURIDAD =====
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # ===== CONFIGURACIÓN DE LOGS =====
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate_required(cls) -> bool:
        """Valida que las configuraciones requeridas estén presentes (compatible con ambas ramas)"""
        errors = []
        
        # Validar OpenAI API Key si se va a usar LLM
        if cls.OPENAI_API_KEY:
            if not cls.OPENAI_API_KEY.startswith('sk-'):
                errors.append("❌ OPENAI_API_KEY debe comenzar con 'sk-'")
        
        # Validar Telegram Bot Token si se va a usar Telegram
        if cls.TELEGRAM_BOT_TOKEN:
            if not cls.TELEGRAM_BOT_TOKEN:
                errors.append("❌ TELEGRAM_BOT_TOKEN es requerido para usar Telegram")
        
        if errors:
            raise ValueError("\n".join(errors))
        
        print("✅ Configuración válida")
        return True
    
    @classmethod
    def get_database_url(cls) -> str:
        """Obtiene la URL de conexión a la base de datos (compatible con Docker y local)"""
        if cls.DATABASE_URL and cls.DATABASE_URL != "mysql://root:admin@db:3306/sportbot_db":
            return cls.DATABASE_URL
        
        # Construir URL desde componentes individuales
        ssl_params = f"?ssl_ca={cls.DB_SSL_CA}" if cls.DB_SSL_CA else ""
        return f"mysql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}{ssl_params}"
    
    @classmethod
    def get_qdrant_config(cls) -> dict:
        """Obtiene la configuración de Qdrant"""
        return {
            "host": cls.QDRANT_HOST,
            "port": cls.QDRANT_PORT,
            "api_key": cls.QDRANT_API_KEY,
            "collection": cls.QDRANT_COLLECTION_NAME
        }
    
    @classmethod
    def get_redis_config(cls) -> dict:
        """Obtiene la configuración de Redis"""
        return {
            "host": cls.REDIS_HOST,
            "port": cls.REDIS_PORT
        }
    
    @classmethod
    def is_docker_environment(cls) -> bool:
        """Determina si estamos en un entorno Docker"""
        return cls.DB_HOST == "db" or "DATABASE_URL" in os.environ
    
    @classmethod
    def get_telegram_config(cls) -> dict:
        """Obtiene la configuración de Telegram"""
        return {
            "bot_token": cls.TELEGRAM_BOT_TOKEN,
            "webhook_url": cls.TELEGRAM_WEBHOOK_URL,
            "bot_name": cls.BOT_NAME
        }
    
    @classmethod
    def get_openai_config(cls) -> dict:
        """Obtiene la configuración de OpenAI"""
        return {
            "api_key": cls.OPENAI_API_KEY,
            "model": cls.OPENAI_MODEL
        }

# Instancia global de configuración
settings = Settings()

# Alias para compatibilidad con código existente (ambas ramas)
Config = settings

# Funciones de compatibilidad para mantener la API existente
def get_database_url() -> str:
    """Obtiene la URL de conexión a la base de datos"""
    return settings.get_database_url()

def get_qdrant_config() -> dict:
    """Obtiene la configuración de Qdrant"""
    return settings.get_qdrant_config()

def get_redis_config() -> dict:
    """Obtiene la configuración de Redis"""
    return settings.get_redis_config()