#!/bin/bash

echo "🔍 Verificando estado de SportBot Assistant..."
echo "=============================================="

# Verificar si Docker está ejecutándose
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está ejecutándose. Por favor, inicia Docker Desktop."
    exit 1
fi

echo "✅ Docker está ejecutándose"

# Verificar estado de los contenedores
echo ""
echo "📊 Estado de los contenedores:"
docker-compose ps

# Verificar si los contenedores están ejecutándose
if ! docker-compose ps | grep -q "Up"; then
    echo ""
    echo "❌ Los contenedores no están ejecutándose."
    echo "Ejecuta: docker-compose up -d"
    exit 1
fi

echo ""
echo "🌐 Verificando servicios..."

# Verificar FastAPI
echo "🔍 Verificando FastAPI..."
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ FastAPI está funcionando en http://localhost:8000"
else
    echo "❌ FastAPI no responde en http://localhost:8000"
fi

# Verificar MySQL
echo "🔍 Verificando MySQL..."
if docker-compose exec -T db mysqladmin ping -h localhost > /dev/null 2>&1; then
    echo "✅ MySQL está funcionando en localhost:3306"
else
    echo "❌ MySQL no responde"
fi

# Verificar Qdrant
echo "🔍 Verificando Qdrant..."
if curl -s http://localhost:6333/collections > /dev/null; then
    echo "✅ Qdrant está funcionando en http://localhost:6333"
else
    echo "❌ Qdrant no responde en http://localhost:6333"
fi

# Verificar Redis
echo "🔍 Verificando Redis..."
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis está funcionando en localhost:6379"
else
    echo "❌ Redis no responde"
fi

echo ""
echo "📋 Información adicional:"
echo "   📚 Documentación API: http://localhost:8000/docs"
echo "   🔍 Qdrant Dashboard: http://localhost:6333/dashboard"
echo "   📊 Logs en tiempo real: docker-compose logs -f"
echo "   🛑 Detener servicios: docker-compose down"

echo ""
echo "🎉 Verificación completada!"
