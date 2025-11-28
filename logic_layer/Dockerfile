# CAMBIO IMPORTANTE: Usamos Python 3.11 en lugar de 3.9
FROM python:3.11-slim

WORKDIR /app

# Instalar git y curl por si son necesarios
RUN apt-get update && apt-get install -y git curl

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "main.py"]