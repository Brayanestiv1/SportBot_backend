#!/bin/bash

# Script de inicio para SportBot con Docker
echo "🚀 Iniciando SportBot Assistant..."

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor, instala Docker primero."
    exit 1
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Por favor, instala Docker Compose primero."
    exit 1
fi

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env desde env.example..."
    cp env.example .env
    echo "✅ Archivo .env creado. Por favor, revisa y ajusta las variables según necesites."
fi

# Construir y levantar los contenedores
echo "🔨 Construyendo contenedores..."
docker-compose build

echo "🚀 Levantando servicios..."
docker-compose up -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 30

# Verificar el estado de los servicios
echo "🔍 Verificando estado de los servicios..."
docker-compose ps

echo ""
echo "✅ SportBot Assistant está iniciando..."
echo ""
echo "📊 Servicios disponibles:"
echo "   🌐 API FastAPI: http://localhost:8000"
echo "   📚 Documentación API: http://localhost:8000/docs"
echo "   🗄️  MySQL: localhost:3306"
echo "   🔍 Qdrant: http://localhost:6333"
echo "   🗃️  Redis: localhost:6379"
echo ""
echo "📋 Comandos útiles:"
echo "   Ver logs: docker-compose logs -f"
echo "   Detener servicios: docker-compose down"
echo "   Reiniciar servicios: docker-compose restart"
echo "   Ver estado: docker-compose ps"
echo ""
echo "🎉 ¡SportBot Assistant está listo para usar!"
