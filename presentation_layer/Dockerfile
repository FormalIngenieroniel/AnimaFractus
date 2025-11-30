FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

# Comando para correr Flask
# host=0.0.0.0 permite acceso externo, port=8501 mantiene consistencia
CMD ["python", "app.py"]