# Este archivo se encarga de indicarle como se ejecutara la aplicacion web dentro
# de la imagen del contenedor al archivo "deploy.sh", se le indica en que directorio
# se creara y con que archivos. Por ultimo indica que se debe correr el archivo 
# "app.py" en el contenedor con el puerto 8501.

FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["python", "app.py"]
