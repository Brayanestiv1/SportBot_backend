@echo off
echo 🔍 Verificando estado de SportBot Assistant...
echo ==============================================

REM Verificar si Docker está ejecutándose
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker no está ejecutándose. Por favor, inicia Docker Desktop.
    pause
    exit /b 1
)

echo ✅ Docker está ejecutándose

REM Verificar estado de los contenedores
echo.
echo 📊 Estado de los contenedores:
docker-compose ps

REM Verificar si los contenedores están ejecutándose
docker-compose ps | findstr "Up" >nul
if errorlevel 1 (
    echo.
    echo ❌ Los contenedores no están ejecutándose.
    echo Ejecuta: docker-compose up -d
    pause
    exit /b 1
)

echo.
echo 🌐 Verificando servicios...

REM Verificar FastAPI
echo 🔍 Verificando FastAPI...
curl -s http://localhost:8000/ >nul 2>&1
if errorlevel 1 (
    echo ❌ FastAPI no responde en http://localhost:8000
) else (
    echo ✅ FastAPI está funcionando en http://localhost:8000
)

REM Verificar MySQL
echo 🔍 Verificando MySQL...
docker-compose exec -T db mysqladmin ping -h localhost >nul 2>&1
if errorlevel 1 (
    echo ❌ MySQL no responde
) else (
    echo ✅ MySQL está funcionando en localhost:3306
)

REM Verificar Qdrant
echo 🔍 Verificando Qdrant...
curl -s http://localhost:6333/collections >nul 2>&1
if errorlevel 1 (
    echo ❌ Qdrant no responde en http://localhost:6333
) else (
    echo ✅ Qdrant está funcionando en http://localhost:6333
)

REM Verificar Redis
echo 🔍 Verificando Redis...
docker-compose exec -T redis redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo ❌ Redis no responde
) else (
    echo ✅ Redis está funcionando en localhost:6379
)

echo.
echo 📋 Información adicional:
echo    📚 Documentación API: http://localhost:8000/docs
echo    🔍 Qdrant Dashboard: http://localhost:6333/dashboard
echo    📊 Logs en tiempo real: docker-compose logs -f
echo    🛑 Detener servicios: docker-compose down

echo.
echo 🎉 Verificación completada!
pause
