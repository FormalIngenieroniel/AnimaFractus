#!/bin/bash

# Definimos nombres para facilitar cambios futuros
IMAGE_NAME="web-app"
CONTAINER_NAME="web_container"
PORT="8501"

# 1. LIMPIEZA DE CONTENEDORES
# Verificamos si existe un contenedor con ese nombre (corriendo o detenido)
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "Deteniendo y eliminando contenedor existente: $CONTAINER_NAME..."
    # Detener (ignora error si ya está detenido)
    docker stop $CONTAINER_NAME >/dev/null 2>&1
    # Eliminar
    docker rm $CONTAINER_NAME
    echo "✅ Contenedor eliminado."
else
    echo "ℹ️ No se encontró contenedor previo con nombre $CONTAINER_NAME."
fi

# 2. LIMPIEZA DE IMÁGENES
# Verificamos si existe la imagen para borrarla y liberar espacio antes del build
if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" != "" ]]; then
    echo "🧹 Eliminando imagen antigua ($IMAGE_NAME) para liberar memoria..."
    docker rmi $IMAGE_NAME
    echo "✅ Imagen eliminada."
fi

# 3. CONSTRUCCIÓN (BUILD)
echo "🏗️ Construyendo nueva imagen..."
# Nota: Asegúrate de que tu archivo se llame 'Dockerfile' y no 'Dockerfile.txt'
if [ -f "Dockerfile.txt" ]; then
    echo "⚠️ Detectado Dockerfile.txt, renombrando a Dockerfile..."
    mv Dockerfile.txt Dockerfile
fi

docker build -t $IMAGE_NAME .

# Verificamos si el build fue exitoso
if [ $? -eq 0 ]; then
    echo "✅ Build exitoso."
else
    echo "❌ Falló el build. Abortando."
    exit 1
fi

# 4. EJECUCIÓN (RUN)
echo "🔥 Levantando contenedor..."
docker run -d --name $CONTAINER_NAME -p $PORT:8501 $IMAGE_NAME


echo "🌍 Tu app disponible en: http://localhost:$PORT"
