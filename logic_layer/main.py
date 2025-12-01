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
# hayan problemas al ingresar otro tipo de dato

class QueryRequest(BaseModel):
    question: str

# Se define el endpoint que se utilizara para hacer la pregunta a los agentes, se comienza
# con la definicion de la base de la peticion

@app.post("/ask")
async def ask_agent(request: QueryRequest):
    print(f"\n📨 SOLICITUD ENTRANTE: {request.question}")
    
    try:
        initial_state = {
            "question": request.question,
            "analysis_logs": [],
            "final_synthesis": ""
        }
        
        # Ejecutamos el grafo
        # invoke devuelve el estado final después de pasar por todos los nodos
        final_state = app_graph.invoke(initial_state)
        
        # Extraemos resultados del estado final
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

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=5000)
