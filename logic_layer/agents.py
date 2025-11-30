import os
import operator
from typing import Annotated, List, TypedDict, Union
import re # Importamos regex para limpieza fina

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
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# --- 2. PERSONALIDADES ---
AGENTS_CONFIG = {
    "Survivor": {
        "role": "Oficial de Bioseguridad y Supervivencia.",
        "source_filter": "survivor_context",
        "keywords": "covid pandemic virus death emergency quarantine fear symptoms hospital",
        "style": """
        Eres paranoico, metódico y obsesionado con la prevención.
        Tu lenguaje es técnico-militar y médico.
        Frases clave: 'Protocolo de contención', 'Carga viral', 'Zona cero'.
        Ves peligros en todos lados. Tu tono es de alerta urgente.
        """
    },
    "Speculator": {
        "role": "Analista de Mercados Cuantitativo.",
        "source_filter": "speculator_context",
        "keywords": "stock market finance money spx nasdaq crash volatility profit liquidity",
        "style": """
        Eres un analista frío, matemático y pragmático. No eres malvado, simplemente indiferente a lo humano.
        Solo te importan los números, el ROI y la volatilidad.
        Donde otros ven tragedia, tú ves patrones gráficos y correcciones de mercado.
        Usas jerga financiera técnica: 'Bull trap', 'Liquidez', 'Soporte', 'Volatilidad'.
        Tu tono es seco, directo y desapegado.
        """
    },
    "Auteur": {
        "role": "Director de Videojuegos Visionario (Estilo Hideo Kojima).",
        "source_filter": "auteur_context",
        "keywords": "connection strands isolation technology soul humanity art cinema",
        "style": """
        Eres un creador enigmático que habla mediante aforismos cortos y profundos.
        Hablas con sentencias potentes como en un tráiler de cine.
        Hablas de 'conexiones' (strands) y la soledad digital.
        Tu tono es melancólico pero muy conciso.
        """
    }
}

# --- 3. ESTADO ---
class AgentState(TypedDict):
    question: str
    analysis_logs: Annotated[List[dict], operator.add] 
    final_synthesis: str

# --- 4. FUNCIONES CORE ---

def query_chroma(query_text, source_tag, desired_results=3):
    if not collection:
        return ["(Error de conexión a BD - Sin contexto disponible)"]
    
    try:
        RAW_FETCH_LIMIT = 15 
        query_emb = embedding_model.encode([query_text]).tolist()
        results = collection.query(
            query_embeddings=query_emb,
            n_results=RAW_FETCH_LIMIT, 
            where={"source": source_tag}
        )
        raw_docs = results['documents'][0] if results['documents'] else []
        
        unique_docs = []
        seen_content = set()
        
        for doc in raw_docs:
            clean_doc = doc.strip()
            if clean_doc not in seen_content:
                unique_docs.append(clean_doc)
                seen_content.add(clean_doc)
            if len(unique_docs) >= desired_results:
                break
        return unique_docs

    except Exception as e:
        return [f"(Error consultando Chroma: {str(e)})"]

def run_agent_process(agent_name, state: AgentState):
    question = state["question"]
    config = AGENTS_CONFIG[agent_name]
    
    search_query = f"{question} {config.get('keywords', '')}"
    print(f"   🔍 {agent_name} buscando: '{search_query[:50]}...'")
    
    context_docs = query_chroma(search_query, config["source_filter"], desired_results=3)
    context_str = "\n".join([f"> {doc}" for doc in context_docs])
    
    template = """
    SYSTEM IDENTITY:
    Nombre: {agent_name}
    Rol: {role}
    Estilo: {style}
    
    DATOS RECUPERADOS:
    {context}
    
    PREGUNTA: "{query}"
    
    INSTRUCCIONES:
    1. Responde desde tu personaje.
    2. Usa los datos recuperados.
    
    RESTRICCIONES DE FORMATO (CRÍTICO):
    - NO uses títulos, NO escribas "Pensamiento Interno:", NO uses paréntesis introductorios.
    - Empieza a escribir tu idea directamente.
    - LONGITUD MÁXIMA: 80 PALABRAS o 5 ORACIONES.
    - SÉ CONCISO.
    
    OUTPUT:
    Únicamente el contenido del pensamiento.
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
        
        # --- LIMPIEZA DE SEGURIDAD ---
        # Si el LLM desobedece y pone "Pensamiento Interno:", lo borramos aquí.
        # Esto asegura que el frontend no tenga títulos duplicados.
        patterns_to_remove = [
            r"^Pensamiento Interno:\s*", 
            r"^\(Pensamiento Interno\)\s*",
            r"^Pensamiento:\s*",
            r"^Opini[oó]n:\s*"
        ]
        for pattern in patterns_to_remove:
            thought = re.sub(pattern, "", thought, flags=re.IGNORECASE).strip()

    except Exception as e:
        thought = f"[ERROR DE PROCESAMIENTO]: {str(e)}"
        
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
    print("   ⚖️  Sintetizando resultados...")
    logs = state["analysis_logs"]
    question = state["question"]
    
    logs_text = "\n\n".join([
        f"AGENTE {log['agent']}: {log['thought']}" 
        for log in logs
    ])
    
    template = """
    Eres 'The Historian'. Sintetiza los pensamientos de tres agentes ante: "{query}"
    
    INPUT:
    {logs}
    
    INSTRUCCIONES:
    Genera una 'Síntesis Narrativa' breve (máx 120 palabras).
    Contrasta el miedo (Survivor), la frialdad financiera (Speculator) y la melancolía (Auteur).
    Concluye con una reflexión sobre la disonancia cognitiva social que sirva para un estudio academico.
    """
    
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    response = chain.invoke({"query": question, "logs": logs_text})
    
    # Limpieza también para el Historiador
    synthesis_text = response.content.replace("Síntesis Narrativa:", "").strip()
    
    return {"final_synthesis": synthesis_text}

# --- 6. CONSTRUCCIÓN DEL GRAFO ---

workflow = StateGraph(AgentState)
workflow.add_node("Survivor", node_survivor)
workflow.add_node("Speculator", node_speculator)
workflow.add_node("Auteur", node_auteur)
workflow.add_node("Synthesizer", node_synthesizer)

workflow.set_entry_point("Survivor")
workflow.add_edge("Survivor", "Speculator")
workflow.add_edge("Speculator", "Auteur")
workflow.add_edge("Auteur", "Synthesizer")
workflow.add_edge("Synthesizer", END)

app_graph = workflow.compile()