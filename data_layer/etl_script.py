# Este archivo se encarga de extraer los datos de los csv para transformarlos en
# embbedings que se puedan subir a la base de datos. Este archivo solo se debe
# ejecutar una vez.

import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
import os
import sys
from tqdm import tqdm

# Se realiza una configuracion donde se agregan unos meta datos para definir
# el contexto de cada agente segun sus personalidades y funciones. Posteriormente
# se utiliza "tag" para saber a que agente le pertenecen esos datos.
files_config = [
    {
        "path": "datasets/Covid_final.csv", 
        "tag": "survivor_context", 
        "type": "covid"
    },
    {
        "path": "datasets/Disasters_final.csv", 
        "tag": "survivor_context", 
        "type": "disaster"
    },
    {
        "path": "datasets/Stocks_final.csv", 
        "tag": "speculator_context", 
        "type": "market"
    },
    {
        "path": "datasets/Kojima_final.csv", 
        "tag": "auteur_context", 
        "type": "social"
    }
]

# Se realiza la conexion a la base de datos haciendo una conexion al contenedor
# que se encuentra en el puerto especificado.
print("⏳ Conectando a ChromaDB en Docker (localhost:8000)...")
try:
    client = chromadb.HttpClient(host='localhost', port=8000)
    print("✅ Conexión exitosa con ChromaDB.")
except Exception as e:
    print(f"❌ Error conectando a ChromaDB. ¿Está corriendo el contenedor Docker? Error: {e}")
    sys.exit(1)

# Si la conexion es exitosa se procede a hacer la conversion de los datos a embbedings
# para poder almacenarlos en la base de datos. Para la conversion se utiliza la
# libreria SentenceTransformer de HuggingFace, donde se llama un modelo que convierta
# los Tweets de los csv. Se utiliza este modelo pues esta enfocado en parrafos cortos
# y frases, lo que aplica para los Tweets
print("⏳ Cargando modelo de Embeddings (esto puede tardar un poco la primera vez)...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Se verifica que la coleccion no exista para evitar problemas.
COLLECTION_NAME = "project_archive"
try:
    client.delete_collection(COLLECTION_NAME)
    print(f"🗑️ Colección '{COLLECTION_NAME}' anterior eliminada.")
except:
    pass

# Se crea la nueva coleccion que contendra todos los datos.
collection = client.create_collection(name=COLLECTION_NAME)
print(f"✨ Nueva colección '{COLLECTION_NAME}' creada.")

# Se realiza el proceso de ETL, se especifica que se haga en un batch de 500 poder
# ver como evoluciona el proceso y verificr que no haya algun crash de la instancia
# EC2.
print("\n🚀 INICIANDO INGESTA DE DATOS...\n")
BATCH_SIZE = 500

# Se inicia el bucle principal, donde se reciben los metadatos asociados al inicio
# del codigo de cada archivo csv. 
for item in files_config:
    file_path = item["path"]
    tag = item["tag"]
    data_type = item["type"]
    
    print(f"📂 Procesando archivo: {file_path} (Etiqueta: {tag})")  
    if not os.path.exists(file_path):
        print(f"   ⚠️ ALERTA: No se encontró el archivo {file_path}. Saltando...")
        continue
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"   ❌ Error leyendo CSV: {e}")
        continue

    # Luego de encontrar el archivo se declaran las listas que contendran la
    # informacion que se convertira a embbeding. Para encontrar la informacion
    # se hace una pequeña busqueda dentro de las columnas del csv, aunque
    # todas las columnas se llaman igual en todos los archivos, se agrega una
    # opcion en caso de que se suba un csv con columnas que se llamen diferente.
    all_ids = []
    all_documents = []
    all_metadatas = []

    print(f"   ⚙️  Preparando datos de {len(df)} filas...")
    count = 0
    for index, row in df.iterrows():
        text_content = row.get('tweet') or row.get('text') or row.get('content')
        date_content = row.get('date') or row.get('timestamp')
        loc_content = row.get('location') or row.get('place') or "Unknown"
        
        if not isinstance(text_content, str):
            continue 
            
        meta = {
            "source": tag,
            "type": data_type,
            "date": str(date_content),
            "location": str(loc_content)
        }
        
        unique_id = f"{data_type}_{index}"

        all_ids.append(unique_id)
        all_documents.append(text_content)
        all_metadatas.append(meta)
        count += 1

    # Se generan los embbedings de todos los documentos que han sido guardados
    # en las listas. Lo hace a traves de paquetes de longitud 500, donde se 
    # registran las diferentes listas para codificar el texto principal y subir
    # paquete con toda la informacion de cada entrada a ChromaDB
    total_docs = len(all_documents)
    if total_docs > 0:
        print(f"   🧠 Generando embeddings e insertando en lotes de {BATCH_SIZE}...")
        
        for i in range(0, total_docs, BATCH_SIZE):
            end_i = min(i + BATCH_SIZE, total_docs)
            batch_docs = all_documents[i:end_i]
            batch_ids = all_ids[i:end_i]
            batch_meta = all_metadatas[i:end_i]
            
            batch_embeddings = embedding_model.encode(batch_docs).tolist()
            
            collection.add(
                ids=batch_ids,
                documents=batch_docs,
                embeddings=batch_embeddings,
                metadatas=batch_meta
            )
            
            progress = (end_i / total_docs) * 100
            print(f"      Status: {end_i}/{total_docs} ({progress:.2f}%) completado.")
            
        print(f"   ✅ Archivo completado exitosamente.")
    else:
        print("   ⚠️ El archivo estaba vacío o no contenía texto válido.")

print("\n🏁 PROCESO COMPLETADO. La base de datos está lista.")
