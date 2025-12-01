# Se utiliza este archivo de la aplicacion de Flask para poder levantar la pagina web de HTML,
# cuando se corre el archivo "deploy.sh" sigue las instrucciones que hay en el "Dockerfile".
# Este le indica que cuando se corra el contenedor debe ejecutarse este archivo en la imagen,
# de esta manera, la aplicacion web se renderiza en un servidor de Flask, no se compila.

from flask import Flask, render_template, request, jsonify
import requests

# Se definen componentes claves como el tipo de la aplicacion y la direccion de la instancia
# que tiene la logica del proyecto, esta se hace mediante peticiones POST desde el front.

app = Flask(__name__)
LOGIC_HOST_IP = "172.31.70.154"
API_URL = f"http://{LOGIC_HOST_IP}:5000/ask"

# Se define la ruta que utilizara la aplicacion para servir el codigo de HTML y poder
# renderizar la aplicacion web dentro de la imagen del contenerdor.

@app.route('/')
def home():
    """Sirve la página principal (HTML)"""
    return render_template('index.html')

# Se define la peticion post que indicara de que manera se enviara la peticion al backend.

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
        response = requests.post(API_URL, json={"question": user_query}, timeout=60)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": f"Logic Layer Error: {response.status_code}"}), 500

    except requests.exceptions.ConnectionError:
        return jsonify(generate_mock_response(user_query))
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Se define una funcion que evita que la aplicacion se caiga si hay un problema con la conexion
# a la logica del backend, es facil de indentificar pues si se analizan los datos recuperados
# de la base de datos, se podra observar que indican que algo fallo.

def generate_mock_response(query):
    """Genera datos falsos para probar la interfaz si el backend falla"""
    lorem = "En los archivos del olvido, la verdad es una moneda de dos caras... " * 10
    return {
        "logs": [
            {"agent": "Survivor", "thought": f"Protocolo de seguridad comprometido. {lorem}", "context_used": ["Resultado inventado", "Resultado inventado", "Resultado inventado"]},
            {"agent": "Speculator", "thought": f"El riesgo calculado excede el margen. {lorem}", "context_used": ["Resultado inventado", "Resultado inventado", "Resultado inventado"]},
            {"agent": "Auteur", "thought": f"La narrativa colapsa sobre sí misma. {lorem}", "context_used": ["Resultado inventado", "Resultado inventado", "Resultado inventado"]},
        ],
        "synthesis": f"El Historiador concluye: Se cayo produccion, es hora de revisar que ocurrio. {lorem}"
    }

# Se define la manera en la que se va a ejecutar el servidor web de Flask

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8501)
