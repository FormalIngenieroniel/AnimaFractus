# Este archivo se encarga de probar si se puede hacer una conexion a la instancia EC2 
# que contiene la base de datos (Instancia A). Se enlaza al puerto donde estan los datos
# y busca la coleccion del proyecto, devuelve informacion acerca de este proceso.

import chromadb
import sys

IP_INSTANCIA_A = "172.31.13.85"
PUERTO = 8000

print(f"📡 Intentando conectar a ChromaDB en {IP_INSTANCIA_A}:{PUERTO}...")

try:
    client = chromadb.HttpClient(host=IP_INSTANCIA_A, port=PUERTO)

    collections = client.list_collections()
    print("✅ ¡CONEXIÓN EXITOSA!")
    print(f"📂 Colecciones encontradas: {[c.name for c in collections]}")

    expected = "project_archive"
    if any(c.name == expected for c in collections):
        print(f"🌟 La colección '{expected}' existe y está lista para ser consultada.")
    else:
        print(f"⚠️ Conectó, pero no encontró la colección '{expected}'. Revisar el archivo ETL de la capa de datos.")

except Exception as e:
    print("\n❌ FALLÓ LA CONEXIÓN")
    print(f"Error: {e}")
    sys.exit(1)
