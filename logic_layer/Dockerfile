# Se utiliza Python 3.11 en lugar de 3.9 para evitar problemas de compatibilidad

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git curl

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "main.py"]
