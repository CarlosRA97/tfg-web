# Imagen base con Python
FROM python:3.11-slim-buster

# Directorio de trabajo
WORKDIR /app

# Copiar el archivo de requerimientos
COPY requirements.txt requirements.txt

# Instalar dependencias (FastAPI y Uvicorn)
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente de la API
COPY . .

EXPOSE 8000

ENTRYPOINT ["fastapi", "run", "api.py"]
