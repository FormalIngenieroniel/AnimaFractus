#!/bin/bash

# En este archivo se define el proceso paa poder correr la aplicacion web.

IMAGE_NAME="web-app"
CONTAINER_NAME="web_container"
PORT="8501"

# Primero se realiza una comprobacion para verificar si existe un contenedor con el mismo nombre 
# ya sea que este corriendo o este detenido. En caso de que exista se detiene y se elimina para
# evitar problemas.

if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "Deteniendo y eliminando contenedor existente: $CONTAINER_NAME..."
    docker stop $CONTAINER_NAME >/dev/null 2>&1
    docker rm $CONTAINER_NAME
    echo "✅ Contenedor eliminado."
else
    echo "ℹ️ No se encontró contenedor previo con nombre $CONTAINER_NAME."
fi

# De la misma manera se hace una verificamos de si existe una imagen previa, en caso de existir
# se borra y se libera el espacio antes de realizar el build.

if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" != "" ]]; then
    echo "🧹 Eliminando imagen antigua ($IMAGE_NAME) para liberar memoria..."
    docker rmi $IMAGE_NAME
    echo "✅ Imagen eliminada."
fi

# Se construye la imagen y se verifica del exito de esta operacion. De ser exitosa, se levanta
# la imagen en el puerto 8501. En la instancia EC2 se permite el trafico utilizando 0.0.0.0
# en el security group para poder acceder con la direccion DNS publica.

echo "🏗️ Construyendo nueva imagen..."
docker build -t $IMAGE_NAME .

if [ $? -eq 0 ]; then
    echo "✅ Build exitoso."
else
    echo "❌ Falló el build. Abortando."
    exit 1
fi

echo "Levantando contenedor..."
docker run -d --name $CONTAINER_NAME -p $PORT:8501 $IMAGE_NAME
echo "🌍 Lu app esta disponible en: http://localhost:$PORT"
