import chromadb

print("⏳ Conectando a la memoria...")
client = chromadb.HttpClient(host='localhost', port=8000)
collection = client.get_collection("project_archive") # <-- NOTA: Usamos get_collection, no create

print(f"✅ Memoria cargada. Total de recuerdos: {collection.count()}")

# Hacemos una pregunta de prueba
query_text = "What happens if there is a pandemic?" 
# O en español si tus datos son en español, aunque vi que eran en inglés mayormente.

print(f"\n🔎 Buscando: '{query_text}'")

results = collection.query(
    query_texts=[query_text],
    n_results=3 # Traer los 3 mejores resultados
)

print("\nResultados encontrados:")
for i, doc in enumerate(results['documents'][0]):
    metadata = results['metadatas'][0][i]
    print(f"--- Resultado {i+1} (Fuente: {metadata['source']}) ---")
    print(doc)
    print("----------------------------------------------------")