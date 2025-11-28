import os
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# --- CONFIGURACIÓN ---
# Conexión a ChromaDB (Capa de Datos)
# Si corres todo en local/mismo docker network usa el nombre del container o IP
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

# Modelo de Embeddings (Debe ser el mismo que usaste en el ETL)
print("🧠 Cargando modelo de embeddings para consultas...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Configuración de Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# --- DEFINICIÓN DE PERSONAS ---
AGENTS_CONFIG = {
    "Survivor": {
        "role": "Un sobreviviente paranoico y precavido de una pandemia.",
        "source_filter": "survivor_context", # Tag definido en tu ETL
        "style": "Analítico, temeroso, enfocado en salud y seguridad."
    },
    "Speculator": {
        "role": "Un inversor agresivo de criptomonedas y bolsa.",
        "source_filter": "speculator_context",
        "style": "Oportunista, cínico, habla de 'buy the dip' y ganancias."
    },
    "Auteur": {
        "role": "Un creador de videojuegos solitario y filosófico (estilo Kojima).",
        "source_filter": "auteur_context",
        "style": "Poético, melancólico, habla de conexiones y soledad."
    }
}

def query_chroma(query_text, source_tag, n_results=3):
    """Busca documentos relevantes en la DB para un agente específico"""
    if not collection:
        return ["(Error de conexión a BD - Sin contexto)"]
    
    query_emb = embedding_model.encode([query_text]).tolist()
    
    results = collection.query(
        query_embeddings=query_emb,
        n_results=n_results,
        where={"source": source_tag} # Filtra por el 'tag' del agente
    )
    
    documents = results['documents'][0] if results['documents'] else []
    return documents

def run_agent_analysis(agent_name, user_query):
    """Ejecuta el ciclo de pensamiento de un agente"""
    config = AGENTS_CONFIG[agent_name]
    
    # 1. Recuperar Contexto (RAG)
    context_docs = query_chroma(user_query, config["source_filter"])
    context_str = "\n".join([f"- {doc}" for doc in context_docs])
    
    # 2. Prompt para Gemini
    template = """
    Eres el Agente: {agent_name}.
    Tu Rol: {role}
    Tu Estilo: {style}
    
    Contexto recuperado de tus archivos (Base de Datos):
    {context}
    
    Pregunta del usuario: "{query}"
    
    Instrucciones:
    1. Analiza la pregunta basándote SOLAMENTE en tu personalidad y el contexto recuperado.
    2. Genera un pensamiento interno corto (máximo 2 frases) sobre lo que ves en los datos.
    
    Respuesta (Solo el pensamiento):
    """
    
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    
    # 3. Invocar a Gemini
    try:
        response = chain.invoke({
            "agent_name": agent_name,
            "role": config["role"],
            "style": config["style"],
            "context": context_str,
            "query": user_query
        })
        thought = response.content
    except Exception as e:
        thought = f"Error conectando con Gemini: {str(e)}"
        
    return {
        "agent": agent_name,
        "thought": thought,
        "context_used": context_docs # Opcional: para ver qué leyó
    }

def synthesize_results(query, agent_logs):
    """El Orquestador sintetiza los pensamientos en una respuesta final"""
    
    logs_text = "\n".join([f"- {log['agent']}: {log['thought']}" for log in agent_logs])
    
    template = """
    Actúa como un Historiador Digital que sintetiza un debate entre tres IAs.
    
    Pregunta del usuario: "{query}"
    
    Opiniones de los Agentes:
    {logs}
    
    Tarea:
    Escribe una conclusión final (Síntesis) que combine estas visiones contrastantes. 
    Menciona cómo cada agente ve el problema desde su ángulo (Miedo, Dinero, Arte).
    Mantén un tono narrativo y épico.
    """
    
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    
    res = chain.invoke({"query": query, "logs": logs_text})
    return res.content