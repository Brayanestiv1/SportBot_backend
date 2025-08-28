# Usa una imagen base de Python que sea adecuada para construir la aplicación
FROM python:3.12-slim

# Instalar dependencias del sistema y herramientas comunes
# Se añaden las dependencias necesarias para Python y Node.js
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    default-libmysqlclient-dev \
    pkg-config \
    git \
    unzip \
    curl \
    # Instalar Node.js y npm para el frontend de React
    && curl -sL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencia de ambos proyectos
COPY SportBot_backend/requirements.txt ./SportBot_backend/
COPY SportBot_frontend/package*.json ./SportBot_frontend/
COPY SportBot_frontend/package-lock.json ./SportBot_frontend/

# Instalar las dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r ./SportBot_backend/requirements.txt

# Instalar las dependencias de Node.js
RUN npm install --prefix ./SportBot_frontend

# Copiar el resto del código del proyecto
COPY SportBot_backend/ ./SportBot_backend/
COPY SportBot_frontend/ ./SportBot_frontend/

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /SportBot_backend /SportBot_frontend
USER app
