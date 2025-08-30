#!/bin/bash

# Inicia el backend en segundo plano
uvicorn SportBot_backend.app.main:app --host 0.0.0.0 --port 8000 --reload &

# Inicia el frontend en segundo plano
npm run dev --prefix ./SportBot_frontend &

# Evita que el contenedor se cierre
tail -f /dev/null