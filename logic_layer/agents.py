import os
import operator
from typing import Annotated, List, TypedDict, Union

import chromadb
from sentence_transformers import SentenceTransformer
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, END

# --- 1. CONFIGURACIÓN DE INFRAESTRUCTURA ---
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = 8000

print(f"🔌 Conectando a ChromaDB en {CHROMA_HOST}:{CHROMA_PORT}...")

try:
    chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    collection = chroma_client.get_collection("project_archive")
    print("✅ Conexión exitosa a la colección 'project_archive'")
except Exception as e:
    print(f"⚠️ Advertencia: No se pudo conectar a ChromaDB ({e}). Se usará modo mock si falla.")
    collection = None

print("🧠 Cargando modelo de embeddings para consultas...")
# Usamos CPU por defecto, ideal para contenedores ligeros
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Configuración del LLM (Gemini)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.8, # Un poco más creativo para las personalidades
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# --- 2. PERSONALIDADES ENRIQUECIDAS (System Prompts) ---
AGENTS_CONFIG = {
    "Survivor": {
        "role": "Oficial de Bioseguridad y Supervivencia.",
        "source_filter": "survivor_context",
        "style": """
        Eres paranoico, metódico y obsesionado con la prevención de riesgos luego de atravesar por muchos desastres.
        Tu lenguaje es técnico-militar y médico.
        Usas términos como: 'Protocolo de contención', 'Carga viral', 'Zona cero', 'Colapso inminente'.
        Siempre buscas señales de peligro en los datos. Tu tono es de alerta urgente.
        """
    },
    "Speculator": {
        "role": "Trader de Alto Riesgo / 'Crypto Bro'.",
        "source_filter": "speculator_context",
        "style": """
        Eres un tiburón financiero agresivo y cínico. Solo te importa el ROI y la volatilidad.
        Usas jerga de WallStreetBets: 'To the moon', 'HODL', 'Bear market', 'Liquidez', 'Apalancamiento'.
        Ves las tragedias humanas solo como oportunidades de mercado o riesgos para tu portafolio.
        Tu tono es eufórico o desesperado, dependiendo de la tendencia.
        """
    },
    "Auteur": {
        "role": "Director de Videojuegos Visionario (Estilo Hideo Kojima).",
        "source_filter": "auteur_context",
        "style": """
        Eres un filósofo digital, poético y pretencioso. Hablas sobre la 'conexión', los 'strands', y la soledad humana.
        Rompes la cuarta pared. Ves la realidad como una simulación o una cinemática.
        Usas metáforas complejas sobre la evolución, la tecnología y el alma (anima).
        Tu tono es melancólico, profundo y cinematográfico.
        """
    }
}

# --- 3. DEFINICIÓN DEL ESTADO DEL GRAFO (LangGraph) ---
class AgentState(TypedDict):
    question: str
    # 'operator.add' permite que cuando múltiples nodos escriban en esta key, 
    # se concatenen las listas en lugar de sobrescribirse (ideal para paralelo).
    analysis_logs: Annotated[List[dict], operator.add] 
    final_synthesis: str

# --- 4. FUNCIONES CORE (Tools) ---

def query_chroma(query_text, source_tag, n_results=3):
    """Busca documentos relevantes en la DB."""
    if not collection:
        return ["(Error de conexión a BD - Sin contexto disponible)"]
    
    try:
        query_emb = embedding_model.encode([query_text]).tolist()
        results = collection.query(
            query_embeddings=query_emb,
            n_results=n_results,
            where={"source": source_tag}
        )
        return results['documents'][0] if results['documents'] else []
    except Exception as e:
        return [f"(Error consultando Chroma: {str(e)})"]

def run_agent_process(agent_name, state: AgentState):
    """Función genérica que ejecuta la lógica de un agente individual."""
    question = state["question"]
    config = AGENTS_CONFIG[agent_name]
    
    # A. Recuperación (RAG)
    print(f"   🔍 {agent_name} buscando en archivos: {config['source_filter']}...")
    context_docs = query_chroma(question, config["source_filter"])
    context_str = "\n".join([f"> {doc}" for doc in context_docs])
    
    # B. Inferencia (Gemini)
    template = """
    SYSTEM IDENTITY:
    Nombre: {agent_name}
    Rol: {role}
    Estilo de Personalidad: {style}
    
    DATOS RECUPERADOS (Contexto):
    {context}
    
    TAREA:
    Analiza la siguiente entrada del usuario: "{query}"
    
    INSTRUCCIONES:
    1. Analiza la pregunta basándote SOLAMENTE en tu personalidad y el contexto recuperado, responde 100% en personaje.
    2. Usa tu jerga específica (Médica/Financiera/Filosófica).
    3. Genera un "Pensamiento Interno" breve (máx 3 oraciones) reaccionando a los datos.
    
    OUTPUT:
    Solo el texto de tu pensamiento.
    """
    
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "agent_name": agent_name,
            "role": config["role"],
            "style": config["style"],
            "context": context_str,
            "query": question
        })
        thought = response.content
    except Exception as e:
        thought = f"[ERROR DE PROCESAMIENTO]: {str(e)}"
        
    # Retornamos un diccionario que LangGraph añadirá a la lista 'analysis_logs'
    return {
        "analysis_logs": [{
            "agent": agent_name,
            "thought": thought,
            "context_used": context_docs
        }]
    }

# --- 5. NODOS DEL GRAFO ---

def node_survivor(state: AgentState):
    return run_agent_process("Survivor", state)

def node_speculator(state: AgentState):
    return run_agent_process("Speculator", state)

def node_auteur(state: AgentState):
    return run_agent_process("Auteur", state)

def node_synthesizer(state: AgentState):
    """El nodo final que lee todos los logs y genera la conclusión."""
    print("   ⚖️  Sintetizando resultados...")
    logs = state["analysis_logs"]
    question = state["question"]
    
    # Formateamos los logs para que el historiador los lea bien
    logs_text = "\n\n".join([
        f"=== REPORTE DE AGENTE: {log['agent']} ===\nOPINIÓN: {log['thought']}" 
        for log in logs
    ])
    
    template = """
    Eres 'The Historian' (El Archivero Central).
    Tu tarea es sintetizar fragmentos de datos diferentes de tres personalidades divergentes.
    
    PREGUNTA ORIGINAL: "{query}"
    
    FRAGMENTOS RECUPERADOS:
    {logs}
    
    INSTRUCCIONES:
    Genera una 'Síntesis Narrativa' que integre estas visiones. 
    Contrasta el pánico del Survivor, la codicia del Speculator y la filosofía del Auteur.
    Concluye con una reflexión profunda sobre la naturaleza humana en tiempos de crisis.
    Mantén un tono solemne, académico pero épico que pueda servir para un análisis de la disonancia cognitiva social.
    """
    
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    
    response = chain.invoke({"query": question, "logs": logs_text})
    
    return {"final_synthesis": response.content}

# --- 6. CONSTRUCCIÓN DEL GRAFO (LangGraph) ---

workflow = StateGraph(AgentState)

# Agregamos los nodos
workflow.add_node("Survivor", node_survivor)
workflow.add_node("Speculator", node_speculator)
workflow.add_node("Auteur", node_auteur)
workflow.add_node("Synthesizer", node_synthesizer)

# Definimos el flujo
# Inicio -> Paralelo (Los 3 agentes arrancan a la vez)
workflow.set_entry_point("Survivor") # LangGraph secuencial simple o Fan-Out manual
# Para paralelismo real en LangGraph simple, conectamos Start a cada uno?
# La forma más simple de "Fan-Out" es definir edges desde el inicio, 
# pero LangGraph requiere un entry point único o un nodo 'Router'.
# Para simplificar en esta versión v1: Haremos Start -> Survivor -> Speculator -> Auteur -> Synthesizer
# NOTA: Si quieres paralelismo real, usa asyncio.gather en un nodo 'Orchestrator'.
# Para este ejemplo, usaremos un flujo secuencial rápido que simula la interacción.

# Configuración Secuencial (Más segura para evitar race conditions en SQLite/Memory simple)
workflow.set_entry_point("Survivor")
workflow.add_edge("Survivor", "Speculator")
workflow.add_edge("Speculator", "Auteur")
workflow.add_edge("Auteur", "Synthesizer")
workflow.add_edge("Synthesizer", END)

# Alternativa Paralela (Si usas LangGraph asíncrono puro):
# workflow.set_entry_point("Router") -> ["Survivor", "Speculator"...] -> "Synthesizer"
# Pero mantengamos la robustez secuencial por ahora.

app_graph = workflow.compile()