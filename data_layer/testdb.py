# Este archivo se ejecuta en la consola para probar si sirve la base de datos luego de 
# crear el container con Docker, principalmente intenta acceder a ella buscando la
# coleccion que se creó en el puerto especificado.

import chromadb

# Se establece el puerto y la coleccion que se quiere buscar
print("⏳ Conectando a la memoria...")
client = chromadb.HttpClient(host='localhost', port=8000)
collection = client.get_collection("project_archive")

print(f"✅ Memoria cargada. Total de recuerdos: {collection.count()}")

# Se hace un pregunta de prueba para probar el acceso a la base de datos
query_text = "What happens if there is a pandemic?" 

print(f"\n🔎 Buscando: '{query_text}'")

# Se encuentran los 3 primeros resultados segun la similitud de la pregunta
results = collection.query(
    query_texts=[query_text],
    n_results=3
)

# Se imprimen los resultados obtenidos
print("\nResultados encontrados:")
for i, doc in enumerate(results['documents'][0]):
    metadata = results['metadatas'][0][i]
    print(f"--- Resultado {i+1} (Fuente: {metadata['source']}) ---")
    print(doc)
    print("----------------------------------------------------")
