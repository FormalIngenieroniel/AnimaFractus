from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# --- CONFIGURACIÓN ---
# IP de tu Logic Layer (Igual que antes)
LOGIC_HOST_IP = "172.31.70.154"
API_URL = f"http://{LOGIC_HOST_IP}:5000/ask"

@app.route('/')
def home():
    """Sirve la página principal (HTML)"""
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_logic_layer():
    """
    Recibe la pregunta del frontend (JS), la envía al Logic Layer,
    y devuelve la respuesta al frontend.
    """
    data = request.json
    user_query = data.get('question')

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Hacemos la petición al servicio de IA (Logic Layer)
        response = requests.post(API_URL, json={"question": user_query}, timeout=60)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": f"Logic Layer Error: {response.status_code}"}), 500

    except requests.exceptions.ConnectionError:
        # Mock/Simulación por si la API real está apagada (Para que puedas probar la UI)
        return jsonify(generate_mock_response(user_query))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_mock_response(query):
    """Genera datos falsos para probar la interfaz si el backend falla"""
    lorem = "En los archivos del olvido, la verdad es una moneda de dos caras... " * 10
    return {
        "logs": [
            {"agent": "Survivor", "thought": f"Protocolo de seguridad comprometido. {lorem}", "context_used": ["Log A", "Log B"]},
            {"agent": "Speculator", "thought": f"El riesgo calculado excede el margen. {lorem}", "context_used": ["Table 1"]},
            {"agent": "Auteur", "thought": f"La narrativa colapsa sobre sí misma. {lorem}", "context_used": ["Essay 4"]},
        ],
        "synthesis": f"El Historiador concluye: La disonancia es total. {lorem}"
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8501)