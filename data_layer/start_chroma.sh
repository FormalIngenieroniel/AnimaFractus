#!/bin/bash

# Este archivo se encarga de ejecutar los comandos necesarios para levantar
# el container que tendra la base de datos.

# Se inicia especificando el nombre del contenedor, el puerto donde estara 
# disponible y por ultimo el nombre del volumen. El cual permitira que los
# datos no se borren a pesar de que se apague la instancia.
CONTAINER_NAME="chroma_server_persistent"
CHROMA_PORT="8000"
VOLUME_NAME="chroma_data"

# Se comprueba si el volumen esta creado, de lo contrario crea uno.
echo "Comprobando si el volumen '$VOLUME_NAME' existe..."
docker volume create $VOLUME_NAME 

# Se comprueba si el contenedor ya existe (corriendo o detenido), si lo
# encuentra, se inicia. Si no existe, se crea.
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
    docker run -d \
        --name $CONTAINER_NAME \
        -p $CHROMA_PORT:8000 \
        -v $VOLUME_NAME:/chroma/chroma \
        -e IS_PERSISTENT=TRUE \
        -e CHROMA_SERVER_DATA_PATH=/chroma/chroma \
        chromadb/chroma:latest
fi

# Se imprime la informacion de docker para comprobar la ejecucion.
echo "--- Estado de Docker ---"
docker ps -f name=$CONTAINER_NAME
