#!/bin/bash

# --- CONFIGURACIÓN ---
CONTAINER_NAME="chroma_server_persistent"
CHROMA_PORT="8000"
# Define el volumen para guardar los datos de ChromaDB de forma permanente
# Esto guarda los datos fuera del ciclo de vida del contenedor
VOLUME_NAME="chroma_data"

# --- EJECUCIÓN ---

echo "Comprobando si el volumen '$VOLUME_NAME' existe..."
# Crea el volumen si no existe
docker volume create $VOLUME_NAME 

echo "Comprobando si el contenedor '$CONTAINER_NAME' ya está corriendo o existe..."

# 1. Comprueba si el contenedor ya existe
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    # Si existe, intenta iniciarlo
    if [ "$(docker ps -aq -f status=exited -f name=$CONTAINER_NAME)" ]; then
        echo "Contenedor existente encontrado (detenido). Iniciando..."
        docker start $CONTAINER_NAME
    else
        echo "Contenedor '$CONTAINER_NAME' ya está corriendo. ¡Listo!"
    fi
else
    # 2. Si no existe, lo crea con el volumen
    echo "Contenedor no encontrado. Creando y ejecutando por primera vez..."
    docker run -d \
        --name $CONTAINER_NAME \
        -p $CHROMA_PORT:8000 \
        -v $VOLUME_NAME:/app/chroma \
        chromadb/chroma:latest
fi

# Muestra el estado para confirmar
echo "--- Estado de Docker ---"
docker ps -f name=$CONTAINER_NAME