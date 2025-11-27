import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
import os
import sys
from tqdm import tqdm

# --- 1. CONFIGURACIÓN: Mapeo de Archivos a Agentes ---
# Aquí definimos qué archivo pertenece a qué "Personalidad".
# 'path': Ruta relativa al archivo CSV.
# 'tag': La etiqueta que usará el Agente para filtrar (source).
# 'type': Un subtipo para diferenciar datos internamente.

files_config = [
    # DATOS PARA EL AGENTE A: THE SURVIVOR (Covid + Desastres)
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
    
    # DATOS PARA EL AGENTE B: THE SPECULATOR (Acciones/Mercados)
    {
        "path": "datasets/Stocks_final.csv", 
        "tag": "speculator_context", 
        "type": "market"
    },
    
    # DATOS PARA EL AGENTE C: THE AUTEUR (Hideo Kojima)
    {
        "path": "datasets/Kojima_final.csv", 
        "tag": "auteur_context", 
        "type": "social"
    }
]

# --- 2. CONFIGURACIÓN DE LA BASE DE DATOS Y MODELO ---

print("⏳ Conectando a ChromaDB en Docker (localhost:8000)...")
# Conectamos al contenedor de Docker que está corriendo en el puerto 8000
try:
    client = chromadb.HttpClient(host='localhost', port=8000)
    print("✅ Conexión exitosa con ChromaDB.")
except Exception as e:
    print(f"❌ Error conectando a ChromaDB. ¿Está corriendo el contenedor Docker? Error: {e}")
    sys.exit(1)

# Inicializamos el modelo de Embeddings (corre local en CPU)
print("⏳ Cargando modelo de Embeddings (esto puede tardar un poco la primera vez)...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Reiniciamos la colección para evitar datos duplicados si corres el script varias veces
COLLECTION_NAME = "project_archive"
try:
    client.delete_collection(COLLECTION_NAME)
    print(f"🗑️ Colección '{COLLECTION_NAME}' anterior eliminada.")
except:
    pass # Si no existía, no pasa nada

# Creamos la colección nueva
collection = client.create_collection(name=COLLECTION_NAME)
print(f"✨ Nueva colección '{COLLECTION_NAME}' creada.")

# --- 3. BUCLE DE PROCESAMIENTO (ETL) ---

print("\n🚀 INICIANDO INGESTA DE DATOS...\n")

BATCH_SIZE = 500  # Procesaremos de 500 en 500 para ver el avance

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
        # --- OPCIONAL: SI QUIERES HACER UNA PRUEBA RÁPIDA DESCOMENTA LA LÍNEA DE ABAJO ---
        # df = df.head(100) # Solo procesa las primeras 100 filas para probar
    except Exception as e:
        print(f"   ❌ Error leyendo CSV: {e}")
        continue

    # Listas globales del archivo
    all_ids = []
    all_documents = []
    all_metadatas = []

    # 1. PREPARACIÓN DE DATOS (Rápido)
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

    # 2. GENERACIÓN DE EMBEDDINGS E INGESTA POR LOTES (Lento, pero con feedback)
    total_docs = len(all_documents)
    if total_docs > 0:
        print(f"   🧠 Generando embeddings e insertando en lotes de {BATCH_SIZE}...")
        
        # Iteramos en pasos de BATCH_SIZE
        for i in range(0, total_docs, BATCH_SIZE):
            # Recortamos el lote actual
            end_i = min(i + BATCH_SIZE, total_docs)
            batch_docs = all_documents[i:end_i]
            batch_ids = all_ids[i:end_i]
            batch_meta = all_metadatas[i:end_i]
            
            # Generamos embeddings solo para este lote
            batch_embeddings = embedding_model.encode(batch_docs).tolist()
            
            # Subimos a ChromaDB
            collection.add(
                ids=batch_ids,
                documents=batch_docs,
                embeddings=batch_embeddings,
                metadatas=batch_meta
            )
            
            # Imprimimos progreso porcentaje simple
            progress = (end_i / total_docs) * 100
            print(f"      Status: {end_i}/{total_docs} ({progress:.2f}%) completado.")
            
        print(f"   ✅ Archivo completado exitosamente.")
    else:
        print("   ⚠️ El archivo estaba vacío o no contenía texto válido.")

print("\n🏁 PROCESO COMPLETADO. La base de datos está lista.")