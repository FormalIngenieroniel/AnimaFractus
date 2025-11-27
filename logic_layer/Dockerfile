FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema si son necesarias
RUN apt-get update && apt-get install -y git

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exponer puerto lógico
EXPOSE 5000

# Comando de arranque
CMD ["python", "main.py"]