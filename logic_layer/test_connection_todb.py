import chromadb
import sys

# --- CONFIGURA AQUÍ LA IP DE LA INSTANCIA A ---
IP_INSTANCIA_A = "172.31.13.85"  # <--- PEGA AQUÍ LA IP DEL PASO 1
PUERTO = 8000

print(f"📡 Intentando conectar a ChromaDB en {IP_INSTANCIA_A}:{PUERTO}...")

try:
    # Intenta conectar como cliente HTTP
    client = chromadb.HttpClient(host=IP_INSTANCIA_A, port=PUERTO)

    # Prueba de fuego: Listar colecciones
    collections = client.list_collections()
    print("✅ ¡CONEXIÓN EXITOSA!")
    print(f"📂 Colecciones encontradas: {[c.name for c in collections]}")

    # Verificar si existe la colección del proyecto
    expected = "project_archive"
    if any(c.name == expected for c in collections):
        print(f"🌟 La colección '{expected}' existe y está lista para ser consultada.")
    else:
        print(f"⚠️ Conectó, pero no encontró la colección '{expected}'. ¿Corriste el ETL en la instancia A?")

except Exception as e:
    print("\n❌ FALLÓ LA CONEXIÓN")
    print(f"Error: {e}")
    sys.exit(1)