# Configuración Unificada - SportBot Assistant

Este documento explica cómo usar la configuración unificada que combina las funcionalidades de Docker y las nuevas características de Telegram/LLM.

## 🎯 Configuración Unificada

La configuración está diseñada para funcionar con **ambas ramas** sin conflictos:

- ✅ **Rama Docker**: Containerización completa
- ✅ **Rama Telegram**: Bot de Telegram + LLM
- ✅ **Compatibilidad total**: Ambas funcionalidades en un solo archivo

## 📁 Archivo de Configuración

### `app/config.py`

```python
from app.config import settings, Config

# Ambas formas funcionan (compatibilidad)
print(settings.APP_NAME)  # Nueva forma
print(Config.APP_NAME)    # Forma original (alias)
```

## 🔧 Configuración para Docker

### Variables de Entorno (Docker)
```bash
# Base de datos (Docker)
DATABASE_URL=mysql://root:admin@db:3306/sportbot_db

# Qdrant (Docker)
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Redis (Docker)
REDIS_HOST=redis
REDIS_PORT=6379
```

### Uso en Código
```python
# Detectar entorno Docker
if settings.is_docker_environment():
    print("✅ Ejecutando en Docker")

# Obtener configuración de base de datos
database_url = settings.get_database_url()

# Obtener configuración de Qdrant
qdrant_config = settings.get_qdrant_config()

# Obtener configuración de Redis
redis_config = settings.get_redis_config()
```

## 🤖 Configuración para Telegram

### Variables de Entorno (Telegram)
```bash
# Bot de Telegram
TELEGRAM_BOT_TOKEN=your-bot-token-here
TELEGRAM_WEBHOOK_URL=https://your-domain.com/webhook
BOT_NAME=SportBot
```

### Uso en Código
```python
# Obtener configuración de Telegram
telegram_config = settings.get_telegram_config()

bot_token = telegram_config['bot_token']
webhook_url = telegram_config['webhook_url']
bot_name = telegram_config['bot_name']
```

## 🧠 Configuración para OpenAI/LLM

### Variables de Entorno (OpenAI)
```bash
# OpenAI
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
```

### Uso en Código
```python
# Obtener configuración de OpenAI
openai_config = settings.get_openai_config()

api_key = openai_config['api_key']
model = openai_config['model']

# Configuración de embeddings
embedding_model = settings.EMBEDDING_MODEL
embedding_dimension = settings.EMBEDDING_DIMENSION
```

## ✅ Validación de Configuración

### Validación Automática
```python
# Validar configuración requerida
try:
    settings.validate_required()
    print("✅ Configuración válida")
except ValueError as e:
    print(f"❌ Errores: {e}")
```

### Validaciones Incluidas
- ✅ **OpenAI API Key**: Verifica formato `sk-`
- ✅ **Telegram Bot Token**: Verifica que esté presente
- ✅ **Configuración de base de datos**: Verifica conectividad
- ✅ **Configuración de Qdrant**: Verifica accesibilidad

## 🔄 Compatibilidad con Código Existente

### Formas de Acceso (Ambas Funcionan)
```python
# Nueva forma (recomendada)
from app.config import settings

# Forma original (compatibilidad)
from app.config import Config

# Ambas apuntan al mismo objeto
assert settings is Config  # True
```

### Propiedades Disponibles
```python
# Configuración de aplicación
settings.APP_NAME
settings.VERSION
settings.DEBUG

# Configuración de servidor
settings.HOST
settings.PORT

# Configuración de base de datos
settings.DB_HOST
settings.DB_PORT
settings.DB_USER
settings.DB_PASSWORD
settings.DB_NAME

# Configuración de Qdrant
settings.QDRANT_HOST
settings.QDRANT_PORT
settings.QDRANT_COLLECTION_NAME

# Configuración de Redis
settings.REDIS_HOST
settings.REDIS_PORT

# Configuración de OpenAI
settings.OPENAI_API_KEY
settings.OPENAI_MODEL

# Configuración de Telegram
settings.TELEGRAM_BOT_TOKEN
settings.TELEGRAM_WEBHOOK_URL
settings.BOT_NAME
```

## 🛠️ Métodos Útiles

### Métodos de Configuración
```python
# Base de datos
settings.get_database_url()

# Qdrant
settings.get_qdrant_config()

# Redis
settings.get_redis_config()

# Telegram
settings.get_telegram_config()

# OpenAI
settings.get_openai_config()

# Detección de entorno
settings.is_docker_environment()

# Validación
settings.validate_required()
```

## 📋 Ejemplo Completo

```python
from app.config import settings

def setup_application():
    """Configuración completa de la aplicación"""
    
    # Validar configuración
    settings.validate_required()
    
    # Configuración de base de datos
    database_url = settings.get_database_url()
    
    # Configuración de servicios
    qdrant_config = settings.get_qdrant_config()
    redis_config = settings.get_redis_config()
    
    # Configuración de Telegram (si está habilitado)
    if settings.TELEGRAM_BOT_TOKEN:
        telegram_config = settings.get_telegram_config()
        print(f"Bot configurado: {telegram_config['bot_name']}")
    
    # Configuración de OpenAI (si está habilitado)
    if settings.OPENAI_API_KEY:
        openai_config = settings.get_openai_config()
        print(f"OpenAI configurado: {openai_config['model']}")
    
    print("✅ Aplicación configurada correctamente")
```

## 🎯 Casos de Uso

### Solo Docker (Sin Telegram/LLM)
```bash
# Solo configurar variables de Docker
DATABASE_URL=mysql://root:admin@db:3306/sportbot_db
QDRANT_HOST=qdrant
REDIS_HOST=redis
```

### Solo Telegram/LLM (Sin Docker)
```bash
# Solo configurar variables de Telegram/LLM
TELEGRAM_BOT_TOKEN=your-token
OPENAI_API_KEY=sk-your-key
DB_HOST=localhost
DB_PORT=3307
```

### Ambos (Docker + Telegram/LLM)
```bash
# Configurar todas las variables
DATABASE_URL=mysql://root:admin@db:3306/sportbot_db
QDRANT_HOST=qdrant
REDIS_HOST=redis
TELEGRAM_BOT_TOKEN=your-token
OPENAI_API_KEY=sk-your-key
```

## ✅ Ventajas de la Configuración Unificada

1. **🔄 Compatibilidad Total**: Funciona con código existente
2. **🎯 Flexibilidad**: Puedes usar solo Docker, solo Telegram, o ambos
3. **🛡️ Validación**: Verificación automática de configuraciones
4. **📝 Documentación**: Métodos claros y bien documentados
5. **🔧 Mantenimiento**: Un solo archivo para todas las configuraciones

¡La configuración unificada te permite usar ambas funcionalidades sin conflictos! 🚀
