import requests
import json

# Probamos contra el localhost de la instancia B
url = "http://localhost:5000/ask"

payload = {
    "question": "¿Cómo cambió la percepción del miedo entre los datos de abril y junio?"
}

print(f"📡 Enviando pregunta a {url}...")
try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        print("\n✅ ¡RESPUESTA RECIBIDA!")
        print("------------------------------------------------")
        print(f"SÍNTESIS: {data.get('synthesis')}")
        print("------------------------------------------------")
        print(f"LOGS ({len(data.get('logs'))} agentes):")
        for log in data.get('logs', []):
            print(f" - [{log['agent']}]: {log['thought']}")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"❌ Falló la conexión: {e}")