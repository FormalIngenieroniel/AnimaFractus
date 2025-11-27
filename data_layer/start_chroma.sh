#!/bin/bash

# --- CONFIGURACIÓN ---
CONTAINER_NAME="chroma_server_persistent"
CHROMA_PORT="8000"
VOLUME_NAME="chroma_data"

# --- EJECUCIÓN ---

echo "Comprobando si el volumen '$VOLUME_NAME' existe..."
docker volume create $VOLUME_NAME 

echo "Comprobando si el contenedor '$CONTAINER_NAME' ya está corriendo o existe..."

if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    if [ "$(docker ps -aq -f status=exited -f name=$CONTAINER_NAME)" ]; then
        echo "Contenedor existente encontrado (detenido). Iniciando..."
        docker start $CONTAINER_NAME
    else
        echo "Contenedor '$CONTAINER_NAME' ya está corriendo. ¡Listo!"
    fi
else
    echo "Contenedor no encontrado. Creando y ejecutando..."
    # AQUI ESTA EL CAMBIO IMPORTANTE
    docker run -d \
        --name $CONTAINER_NAME \
        -p $CHROMA_PORT:8000 \
        -v $VOLUME_NAME:/chroma/chroma \
        -e IS_PERSISTENT=TRUE \
        -e CHROMA_SERVER_DATA_PATH=/chroma/chroma \
        chromadb/chroma:latest
fi

echo "--- Estado de Docker ---"
docker ps -f name=$CONTAINER_NAME