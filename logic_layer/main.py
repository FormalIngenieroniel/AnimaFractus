# Este archivo se encarga de subir la API de toda la logica del proyecto utilizando FastAPI
# corriendo la aplicaion en el puerto 5000, hace el host en 0.0.0.0 porque ya esta configurado
# en AWS el security group para solo permitir conexiones desde la instancia que hostea la app
# web. 

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from agents import app_graph

app = FastAPI()

# Se utiliza pydantic para asegurarnos que la pregunta del usuario siempre sera un str y no
# hayan problemas al ingresar otro tipo de dato, ademas especifica que el campo se llame
# 'question'

class QueryRequest(BaseModel):
    question: str

# Se define el endpoint que se utilizara para hacer la pregunta a los agentes, se comienza
# con la definicion de la base de la peticion siendo esta tipo post, que al ser llamada,
# primero creara la base de la solicitud que se le pasara a cada agente en el "initial_state".
# Esta contendra la pregunta, los diferentes analisis y la sintesis, que seran los resultados
# a mostrar en la web. 
# Se hace el llamado al grafo de procesamiento de los agente que esta en el archivo "agents.py" 
# y almacena la respuesta, con la estructura mencionada anteriormente, en la variable 
# "final_state". La peticion retorna los pensamientos de cada agente y la sintesis.

@app.post("/ask")
async def ask_agent(request: QueryRequest):
    print(f"\n📨 SOLICITUD ENTRANTE: {request.question}")
    
    try:
        initial_state = {
            "question": request.question,
            "analysis_logs": [],
            "final_synthesis": ""
        }
        
        final_state = app_graph.invoke(initial_state)

        # Para facilidad a la hora de trabajar con los datos, se extrae la sintesis y los
        # diferentes analisis de los agentes por separado en las variables "synthesis" y
        # "logs" respectivamente
        
        synthesis = final_state.get("final_synthesis", "Error generando síntesis.")
        logs = final_state.get("analysis_logs", [])
        
        print(f"✅ Proceso completado. Logs generados: {len(logs)}")
        
        return {
            "synthesis": synthesis,
            "logs": logs
        }
        
    except Exception as e:
        print(f"❌ Error Crítico en Logic Layer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Se define la ejecucion que subira la API en un servidor que estara escuchando las peticiones 
# localmente en el puerto 5000

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
