@echo off
echo 🚀 Iniciando SportBot Assistant...

REM Verificar si Docker está instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker no está instalado. Por favor, instala Docker primero.
    pause
    exit /b 1
)

REM Verificar si Docker Compose está instalado
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose no está instalado. Por favor, instala Docker Compose primero.
    pause
    exit /b 1
)

REM Crear archivo .env si no existe
if not exist .env (
    echo 📝 Creando archivo .env desde env.example...
    copy env.example .env
    echo ✅ Archivo .env creado. Por favor, revisa y ajusta las variables según necesites.
)

REM Construir y levantar los contenedores
echo 🔨 Construyendo contenedores...
docker-compose build

echo 🚀 Levantando servicios...
docker-compose up -d

REM Esperar a que los servicios estén listos
echo ⏳ Esperando a que los servicios estén listos...
timeout /t 30 /nobreak >nul

REM Verificar el estado de los servicios
echo 🔍 Verificando estado de los servicios...
docker-compose ps

echo.
echo ✅ SportBot Assistant está iniciando...
echo.
echo 📊 Servicios disponibles:
echo    🌐 API FastAPI: http://localhost:8000
echo    📚 Documentación API: http://localhost:8000/docs
echo    🗄️  MySQL: localhost:3306
echo    🔍 Qdrant: http://localhost:6333
echo    🗃️  Redis: localhost:6379
echo.
echo 📋 Comandos útiles:
echo    Ver logs: docker-compose logs -f
echo    Detener servicios: docker-compose down
echo    Reiniciar servicios: docker-compose restart
echo    Ver estado: docker-compose ps
echo.
echo 🎉 ¡SportBot Assistant está listo para usar!
pause
