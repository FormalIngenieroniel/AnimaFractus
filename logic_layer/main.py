from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from agents import app_graph  # Importamos el grafo compilado

app = FastAPI()

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_agent(request: QueryRequest):
    print(f"\n📨 SOLICITUD ENTRANTE: {request.question}")
    
    try:
        # Estado inicial
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
        # Es buena práctica imprimir el stacktrace en logs reales
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Corremos en 0.0.0.0 para que sea accesible desde otros contenedores
    uvicorn.run(app, host="0.0.0.0", port=5000)