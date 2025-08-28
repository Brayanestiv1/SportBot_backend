# SportBot API - Entorno de Desarrollo

Este proyecto utiliza Docker y VS Code Dev Containers para crear un entorno de desarrollo aislado y reproducible. La API está construida con FastAPI y utiliza una base de datos MySQL, un vector store Qdrant y Redis.

## Archivos Principales

A continuación se explican los archivos clave de configuración de este entorno de desarrollo:

### `Dockerfile`

Este archivo define la imagen de Docker para la API. Está basado en `python:3.12-slim` para mantener el tamaño de la imagen pequeño.

- **Instalación de dependencias:** Se instalan las dependencias del sistema necesarias para compilar paquetes de Python (como `mysqlclient`).
- **Copia de archivos:** Copia el archivo `requirements.txt` para instalar las librerías de Python y luego el resto del código de la aplicación.
- **Creación de usuario `app`:** Por seguridad, la aplicación se ejecuta con un usuario no-root llamado `app`.

### `docker-compose.yml`

Este archivo orquesta los distintos servicios de la aplicación.

- **`app`**: El servicio principal que corre la API de FastAPI. Su contexto de construcción se ha modificado para apuntar a la raíz del proyecto, lo que le permite encontrar el `Dockerfile` y `requirements.txt` correctamente.
- **`db`**: El servicio para la base de datos MySQL, utilizando la imagen `mysql:8.0`. Se configura la base de datos, el usuario y la contraseña. Se exponen los puertos para poder acceder desde el host si es necesario.
- **`qdrant`**: Un vector store que almacena y recupera vectores, esencial para la funcionalidad del chatbot.
- **`redis`**: Un servicio de caché de Redis que puede ser utilizado por la aplicación para mejorar el rendimiento.
- **Redes y volúmenes**: Se definen una red (`sportbot-network`) para la comunicación entre los servicios y volúmenes para la persistencia de datos.

### `devcontainer.json`

Este archivo de configuración es específico para VS Code y los Dev Containers. Le dice a VS Code cómo configurar el entorno de desarrollo.

- **`dockerComposeFile` y `service`**: Apuntan a tu `docker-compose.yml` y al servicio `app` como tu entorno principal.
- **Extensiones de VS Code**: Se listan las extensiones recomendadas para trabajar con Python, Docker, YAML, bases de datos y Git.
- **`postStartCommand`**: Este es el comando más importante. Se ha añadido la línea `"uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"` para iniciar la aplicación FastAPI automáticamente cuando el contenedor se levanta. **Esto es clave para que la API se ejecute.**

## Ejecución de la Aplicación

Para comenzar a trabajar con el proyecto, sigue estos pasos:

1. Asegúrate de tener **Docker** y la extensión de **Dev Containers** de VS Code instalados.
2. Abre el proyecto en VS Code y haz clic en el botón de **"Reopen in Container"** que aparecerá en la esquina inferior derecha. Esto construirá y levantará los servicios de Docker.
3. Una vez que el contenedor esté listo, el `postStartCommand` ejecutará `uvicorn` para iniciar la API.
4. Si todo ha funcionado correctamente, la API estará disponible en `http://localhost:8000`. Ten en cuenta que es posible que haya errores de conexión con la base de datos u otros servicios que debas solucionar una vez que la API esté en funcionamiento.