from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from agents import run_agent_analysis, synthesize_results

app = FastAPI()

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_agent(request: QueryRequest):
    print(f"📨 Recibida pregunta: {request.question}")
    
    try:
        # 1. Ejecutar los 3 agentes en paralelo (o secuencial rápido)
        logs = []
        agent_names = ["Survivor", "Speculator", "Auteur"]
        
        for name in agent_names:
            print(f"   🤖 Consultando Agente: {name}...")
            result = run_agent_analysis(name, request.question)
            logs.append(result)
            
        # 2. Sintetizar respuesta final
        print("   ⚖️  Sintetizando respuesta final...")
        final_synthesis = synthesize_results(request.question, logs)
        
        return {
            "synthesis": final_synthesis,
            "logs": logs
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=5000)