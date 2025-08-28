# SportBot Assistant - Asistente Comercial

Un asistente comercial inteligente construido con FastAPI, Python, Qdrant y MySQL, containerizado con Docker para fácil despliegue y uso.

## ⚡ Instalación Rápida - Solo 2 Comandos

**Para Windows:**
```bash
start.bat          # Instala todo automáticamente
check-status.bat   # Verifica que todo funciona
```

**Para Linux/macOS:**
```bash
./start.sh         # Instala todo automáticamente
./check-status.sh  # Verifica que todo funciona
```

**¿Qué incluye la instalación?**
- ✅ Python 3.12 y todas las dependencias
- ✅ Imagen Docker con tu aplicación FastAPI
- ✅ Base de datos MySQL inicializada
- ✅ Qdrant (base de datos vectorial)
- ✅ Redis (caché)
- ✅ Verificación automática de todos los servicios

## 🚀 Características

- **FastAPI**: API REST moderna y rápida
- **Python 3.12**: Última versión estable de Python
- **Qdrant**: Base de datos vectorial para búsquedas semánticas
- **MySQL 8.0**: Base de datos relacional robusta
- **Redis**: Caché y sesiones (opcional)
- **Docker**: Containerización completa para fácil despliegue

## 📋 Requisitos Previos

- Docker Desktop instalado
- Docker Compose instalado
- Al menos 4GB de RAM disponible
- 10GB de espacio en disco

## 🛠️ Instalación y Uso - ¡Solo 2 Comandos!

### ⚡ Instalación Automática (Recomendado)

**¿Qué hace?** Descarga todas las dependencias, construye la imagen Docker, levanta todos los servicios y verifica que todo funcione.

#### En Windows:
```bash
start.bat
```
**¿Qué incluye?**
- ✅ Descarga Python 3.12 y todas las dependencias
- ✅ Construye la imagen Docker con tu aplicación
- ✅ Levanta MySQL, Qdrant, Redis y FastAPI
- ✅ Crea la base de datos automáticamente
- ✅ Verifica que todo esté funcionando

#### En Linux/macOS:
```bash
chmod +x start.sh
./start.sh
```
**¿Qué incluye?**
- ✅ Descarga Python 3.12 y todas las dependencias
- ✅ Construye la imagen Docker con tu aplicación
- ✅ Levanta MySQL, Qdrant, Redis y FastAPI
- ✅ Crea la base de datos automáticamente
- ✅ Verifica que todo esté funcionando

### Opción 2: Comandos Manuales

1. **Clonar el repositorio:**
```bash
git clone <tu-repositorio>
cd SportBot_backend
```

2. **Crear archivo de variables de entorno:**
```bash
cp env.example .env
# Editar .env según tus necesidades
```

3. **Construir y levantar los contenedores:**
```bash
docker-compose build
docker-compose up -d
```

4. **Verificar que todo esté funcionando:**
```bash
# Opción 1: Script automático de verificación (Recomendado)
check-status.bat  # Windows - Verifica todos los servicios automáticamente
./check-status.sh # Linux/macOS - Verifica todos los servicios automáticamente

# Opción 2: Verificación manual
docker-compose ps  # Muestra el estado de todos los contenedores
curl http://localhost:8000/  # Prueba si la API responde
```

## 🌐 Servicios Disponibles

Una vez iniciado, tendrás acceso a:

- **API FastAPI**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **MySQL**: localhost:3307 (cambiado para evitar conflictos)
- **Qdrant**: http://localhost:6333
- **Redis**: localhost:6379

## ✅ Verificación de Funcionamiento - ¡Solo 1 Comando!

### Verificación Automática (Recomendada)
```bash
# Windows
check-status.bat
```
**¿Qué hace?**
- ✅ Verifica que Docker esté ejecutándose
- ✅ Comprueba que todos los contenedores estén activos
- ✅ Prueba que la API FastAPI responda
- ✅ Verifica que MySQL esté funcionando
- ✅ Comprueba que Qdrant esté disponible
- ✅ Verifica que Redis esté activo
- ✅ Te muestra las URLs para acceder a cada servicio

```bash
# Linux/macOS
./check-status.sh
```
**¿Qué hace?**
- ✅ Verifica que Docker esté ejecutándose
- ✅ Comprueba que todos los contenedores estén activos
- ✅ Prueba que la API FastAPI responda
- ✅ Verifica que MySQL esté funcionando
- ✅ Comprueba que Qdrant esté disponible
- ✅ Verifica que Redis esté activo
- ✅ Te muestra las URLs para acceder a cada servicio

### Verificación Manual
```bash
# 1. Verificar que los contenedores estén ejecutándose
docker-compose ps

# 2. Verificar que la API responda
curl http://localhost:8000/

# 3. Verificar el endpoint de salud
curl http://localhost:8000/health

# 4. Abrir en el navegador
# http://localhost:8000/docs
```

## 👥 Colaboración en Equipo - ¡Solo 2 Comandos!

### Para Desarrolladores Nuevos
1. **Hacer pull de la rama principal**
2. **Ejecutar el script de inicio** según tu sistema operativo
3. **Verificar funcionamiento** con los scripts de verificación
4. **¡Listo para desarrollar!**

### 🚀 Flujo Ultra Simple para tu Equipo

**Paso 1: Instalar todo (1 comando)**
```bash
# Windows
start.bat

# Linux/macOS
./start.sh
```

**Paso 2: Verificar que funciona (1 comando)**
```bash
# Windows
check-status.bat

# Linux/macOS
./check-status.sh
```

**¡Eso es todo! En 2 comandos tienen todo instalado y funcionando.** 🎉

### Compatibilidad Multiplataforma
- ✅ **Windows**: Usa `start.bat` y `check-status.bat`
- ✅ **Linux/macOS**: Usa `start.sh` y `check-status.sh`
- ✅ **Misma configuración** para todos los desarrolladores
- ✅ **No interfiere** con configuraciones locales existentes
- ✅ **Imagen Docker** con todo preconfigurado
- ✅ **Base de datos** inicializada automáticamente

### Puertos Utilizados
- **8000**: API FastAPI (principal)
- **3307**: MySQL (evita conflictos con instalaciones locales)
- **6333**: Qdrant
- **6379**: Redis

## 📁 Estructura del Proyecto

```
SportBot_backend/
├── app/                    # Código de la aplicación
│   ├── main.py            # Punto de entrada FastAPI
│   ├── config.py          # Configuración
│   ├── models/            # Modelos de datos
│   ├── routes/            # Rutas de la API
│   ├── services/          # Lógica de negocio
│   └── controllers/       # Controladores
├── mysql/                 # Scripts de base de datos
│   └── init/              # Scripts de inicialización
├── docker-compose.yml     # Configuración de servicios
├── Dockerfile            # Imagen de la aplicación
├── requirements.txt      # Dependencias de Python
├── start.sh             # Script de inicio (Linux/macOS)
├── start.bat            # Script de inicio (Windows)
├── check-status.sh      # Script de verificación (Linux/macOS)
├── check-status.bat     # Script de verificación (Windows)
├── env.example          # Plantilla de variables de entorno
└── README.md            # Este archivo
```

## 🔧 Comandos Útiles

### Gestión de Imágenes Docker
```bash
# Ver todas las imágenes
docker images

# Ver detalles de la imagen del proyecto
docker images | grep sportbot

# Eliminar imagen (si necesitas reconstruir)
docker rmi sportbot_backend-app

# Ver historial de la imagen
docker history sportbot_backend-app
```

### Gestión de Contenedores
```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f app

# Detener todos los servicios
docker-compose down

# Reiniciar servicios
docker-compose restart

# Ver estado de los servicios
docker-compose ps

# Reconstruir contenedores
docker-compose build --no-cache
```

### Base de Datos
```bash
# Conectar a MySQL
docker-compose exec db mysql -u root -p

# Hacer backup de la base de datos
docker-compose exec db mysqldump -u root -p sportbot_db > backup.sql

# Restaurar backup
docker-compose exec -T db mysql -u root -p sportbot_db < backup.sql
```

### Desarrollo
```bash
# Entrar al contenedor de la aplicación
docker-compose exec app bash

# Instalar nuevas dependencias
docker-compose exec app pip install nueva-dependencia

# Ejecutar tests
docker-compose exec app python -m pytest

# Ejecutar tests con detalle
docker-compose exec app python -m pytest -v

# Ejecutar tests específicos
docker-compose exec app python -m pytest tests/test_api.py -v
```

## 🧪 Testing

El proyecto incluye pruebas unitarias y de integración para todos los endpoints de la API.

### Ejecutar Tests
```bash
# Ejecutar todas las pruebas
python -m pytest tests/ -v

# Ejecutar pruebas específicas
python -m pytest tests/test_api.py -v

# Ejecutar con cobertura
python -m pytest tests/ --cov=app --cov-report=html
```

### Estructura de Tests
```
tests/
├── test_api.py           # Pruebas de endpoints de la API
├── conftest.py           # Configuración de fixtures (futuro)
└── __init__.py           # Marca el directorio como paquete
```

### Pruebas Incluidas
- ✅ **Endpoint de salud** (`GET /health`)
- ✅ **Endpoint de chat** (`POST /chats/message`)
- ✅ **Webhook de Telegram** (`POST /telegram/webhook`)
- ✅ **Endpoints de administración** (verificación de 404)
- ✅ **Validación de datos** y casos de error
- ✅ **Mocking de servicios externos** (LLM, Telegram)

### Dependencias de Testing
Las siguientes dependencias están incluidas en `requirements.txt`:
- `pytest==8.2.2` - Framework de testing
- `pytest-asyncio==0.24.0` - Soporte para tests async
- `httpx==0.28.1` - Cliente HTTP para testing (incluido con FastAPI)

### Ejecutar Tests en Docker
```bash
# Dentro del contenedor
docker-compose exec app python -m pytest tests/ -v

# Desde fuera del contenedor
docker-compose exec app bash -c "python -m pytest tests/ -v"
```

## 🔒 Configuración de Seguridad

### Variables de Entorno Importantes

Edita el archivo `.env` para configurar:

- `SECRET_KEY`: Clave secreta para JWT
- `MYSQL_ROOT_PASSWORD`: Contraseña de MySQL
- `DATABASE_URL`: URL de conexión a la base de datos

### Puertos Expuestos

- **8000**: API FastAPI
- **3306**: MySQL
- **6333**: Qdrant HTTP
- **6334**: Qdrant gRPC
- **6379**: Redis

## 🐛 Solución de Problemas

### Error: Puerto ya en uso
```bash
# Ver qué está usando el puerto
netstat -tulpn | grep :8000

# Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Cambiar 8000 por 8001
```

### Error: Permisos de Docker
```bash
# En Linux, agregar usuario al grupo docker
sudo usermod -aG docker $USER
# Reiniciar sesión
```

### Error: Memoria insuficiente
- Aumentar memoria asignada a Docker Desktop
- Cerrar otras aplicaciones que consuman mucha RAM

### Error: Base de datos no conecta
```bash
# Verificar logs de MySQL
docker-compose logs db

# Reiniciar solo la base de datos
docker-compose restart db
```

## 📈 Monitoreo

### Verificar Salud de la API
```bash
curl http://localhost:8000/health
```

### Verificar Qdrant
```bash
curl http://localhost:6333/collections
```

### Verificar MySQL
```bash
docker-compose exec db mysqladmin ping -h localhost
```

## 🔄 Actualizaciones

Para actualizar el proyecto:

1. **Hacer pull de los cambios:**
```bash
git pull origin main
```

2. **Reconstruir contenedores:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs: `docker-compose logs`
2. Verifica que Docker esté funcionando: `docker --version`
3. Asegúrate de tener suficiente memoria y espacio en disco
4. Revisa que los puertos no estén ocupados

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo LICENSE para más detalles.

---

¡Disfruta usando SportBot Assistant! 🎉