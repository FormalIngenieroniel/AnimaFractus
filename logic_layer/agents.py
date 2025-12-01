# Este archivo contiene la logica pura que se encargara del proceso de hacer las preguntas
# a los diferentes agentes. Contiene las definiciones de los prompts, las personalidades y 
# el flujo de cada uno.

import os
import operator
from typing import Annotated, List, TypedDict, Union
import re
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, END

# Se comienza definiendo la conexion a la instancia EC2 que contiene la base de datos, la 
# direccion y la key de google se encuentran en el archivo de entorno por seguridad. Una
# vez se conecta a la direccion especifica, se busca la coleccion que contiene los datos. 

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

# Se vuelve a cargar el modelo de HuggingFace que se utilizo en el archvio de ETL en la 
# capa de datos para crear los embbedings. Este se utiliza en este caso para poder 
# convertir la pregunta del usuario y posteriormente buscar la similitud en la base de 
# datos.

print("🧠 Cargando modelo de embeddings para consultas...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Se configura el modelo que se utilizara para realizar la generacio nde texto, se utiliza
# LangChain para poder conectarse al modelo especificado de Gemini y ocnfigurarlo de una
# manera facil. Se hace uso de "2.5-flash-lite" para aprovechar su rapidez y que al estar
# utilizando varios agentes las respuestas sean rapidas y consistentes. Se hace uso de una
# temperatura relativamente alta para tener una mayor diversidad en las palabras, en este
# caso practico, para que cada uno de los personajes pueda tener un vocabulario mas variado
# en sus campos y tareas asignadas.

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Se configura el comportamiento que tendra cada agente, este comportamiento para cada uno
# se basa en un rol en especifico, el contexto que se definio en el archivo de ETL, para 
# que cada agente tenga los datos que estan acorde a cada rol. Adicionalmente se agregan
# palabras claves para que cuando se haga la busqueda por similitud, los tweets recuperados
# no se vayan a salir de ese tema en concreto, por este motivo se encuentran en ingles.
# El estilo se encarga de definir como se va a desenvolver la generacion de la respuesta,
# definiendo ciertos terminos y que lenguaje utilizar.

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

# Se define el estado de los agentes en una clase que tiene la pregunta original, una 
# lista de diccionarios que se actualizara con el pensamiento de cada agente gracias a
# "operator.add" que no lo sobre escribe y la sisntesis final del historiador. 

class AgentState(TypedDict):
    question: str
    analysis_logs: Annotated[List[dict], operator.add] 
    final_synthesis: str

# Se define como se hace la busqueda en la base de datos, la funcion toma la pregunta
# que se va a volver embbeding, el filtro del agente y cuantos resultados se quieren
# buscar. Se eligen 3 para evitar sobrecargar el prompt y porque se buscan respuestas
# que no sean muy extensas.

def query_chroma(query_text, source_tag, desired_results=3):

    # Primero se verifica que la coleccion este disponible para realizar la busqueda.
    
    if not collection:
        return ["(Error de conexión a BD - Sin contexto disponible)"]

    # Se define que se quieren extraer 15 tweets, esto se hace porque en algunos casos
    # existen datos duplicados, la extraccion de los 15 es para evitar este problema
    # y solo escoger los top 3 datos unicos.
    # Posteriormente se convierte la consulta a embbeding para poder realizar la 
    # busqueda por similaridad, a esta busqueda se le pasa la pregunta, el numero de
    # cuantos se quiere recuperar y por, ultimo el filtro del agente.
    
    try:
        RAW_FETCH_LIMIT = 15 
        query_emb = embedding_model.encode([query_text]).tolist()
        results = collection.query(
            query_embeddings=query_emb,
            n_results=RAW_FETCH_LIMIT, 
            where={"source": source_tag}
        )

        # Se obtinen los resultados como una lista de strings, se inicializa una lista 
        # y un set para almacenar los datos duplicados, se usa una lista para mantener
        # el orden de insercion y un set para operaciones rapidas de verificacion.
        
        raw_docs = results['documents'][0] if results['documents'] else []
        unique_docs = []
        seen_content = set()

        # Se intera en los documentos obtenidos, primero se hace una limpieza del dato
        # y se verifica que no se haya visto con anterioridad, si no se ha visto, se 
        # agrega a los documentos unicos. Hace este proceso hasta que se recuperen los
        # documentos necesarios, en este caso 3.
        
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

# Se define como se hara el proceso de los agentes para construir querys, recuperar 
# el contexto de la base de datos, generar prompts, invocar al LLM, limpiar outputs y 
# como se retorna la respuesta de cada uno.

def run_agent_process(agent_name, state: AgentState):

    # Se extrae la pregunta y el nombre del agente, una vez estos datos son extraidos
    # se procede a definir como se va a hacer la busqueda. Se le agrega a la pregunta
    # las palabras claves que se definieron para hacer mas efectiva y centrada la
    # busqueda. Se llama la funcion antes definida para buscar en la base de datos, 
    # pasandole la busqueda enriquecida, el filtro del agente y la cantidad de documentos
    # deseados. Una vez se optiene una respuesta se le da un formato para tener una 
    # mejor legibilidad.
    
    question = state["question"]
    config = AGENTS_CONFIG[agent_name]
    
    search_query = f"{question} {config.get('keywords', '')}"
    print(f"   🔍 {agent_name} buscando: '{search_query[:50]}...'")
    
    context_docs = query_chroma(search_query, config["source_filter"], desired_results=3)
    context_str = "\n".join([f"> {doc}" for doc in context_docs])

    # Se define la plantilla del prompt que se le va a pasar al llm. Primero se establece
    # la identidad que va a adquirir, se le da un nombre, rol y estilo. Luego se le pasa
    # como contexto los tweets quese recuperaron. Posteriormente se le pasa la pregunta
    # que se le quiere hacer. Por ultimo de definen algunas reglas, las mas basicas se
    # encuentran en "INSTRUCCIONES" donde se limita al uso del contexto y la personalidad,
    # en "RESTRICCIONES DE FORMATO" se le dan reglas para uniformizar la manera en la que 
    # se devuelve la respuesta para que se vea mas limpio en la pagina web y se define como
    # se quiere tener el output.
    
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

    # Una vez la plantilla esta armada se utiliza LangChain para convertirla en un prompt
    # dinamico y poder ingresarle valores a las variables como "agent_name" en medio de la 
    # ejecucion, esto es importante para asegurar la escalabilidad y la major respuesta
    # posible. Este prompt luego se utiliza en la cadema definida para pasarselo al llm.
    
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm

    # Asi mismo, se realiza la invocacion de la cadena, pasandole los datos claves que se
    # van a reemplazar en el prompt. Esta respuesta se almacena posteriormente en una 
    # variable.

    try:
        response = chain.invoke({
            "agent_name": agent_name,
            "role": config["role"],
            "style": config["style"],
            "context": context_str,
            "query": question
        })
        thought = response.content
        
        # Se utilizan expresiones regulares para limpiar el texto de salida de los diferentes 
        # pensamientos de los agentes. Se realiza este paso para que al recuperar el texto, 
        # se utilice un mismo formato para todas las respuestas y no haya problemas cuando se 
        # muestre el texto en la seccion dedicada en la pagina web.
        
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

    # Finalmente se retornan los resultados que se van a almacenar en los losgs de "AgentState"
    # para tener una buena gestion de la informacion en el grafo y poder hacer una sintesis 
    # final.

    return {
        "analysis_logs": [{
            "agent": agent_name,
            "thought": thought,
            "context_used": context_docs
        }]
    }

# Se definen los diferentes nodos del grafo, cada nodo sera un agente, no se define un nuevo
# prompt para los tres primeros agentes pues cumplen una misma funcion. Para el historiador,
# se necesita definir una nueva tarea para uqe logra sintetizar toda la informacion de los 
# demas agentes.

def node_survivor(state: AgentState):
    return run_agent_process("Survivor", state)

def node_speculator(state: AgentState):
    return run_agent_process("Speculator", state)

def node_auteur(state: AgentState):
    return run_agent_process("Auteur", state)

# Para crear el prompt del sintetizador, primero se recuperan los logs, que deben tener la
# informacion de las respuestas anteriores y la pregunta. Luego por medio de una comprehension
# list, se extraen los nombres de los agentes y sus respuestas de pensamiento, incorporandolo
# en un solo string.

def node_synthesizer(state: AgentState):
    print("   ⚖️  Sintetizando resultados...")
    logs = state["analysis_logs"]
    question = state["question"]
    
    logs_text = "\n\n".join([
        f"AGENTE {log['agent']}: {log['thought']}" 
        for log in logs
    ])

    # De igual manera se construye la plantilla dandole la descripcion de la tarea que debe
    # realizar y algunas instrucciones para que de una respuesta acorde a lo que se busca
    # con el proyecto. Igualmente que en el anterior caso, se convierte la plantilla a un 
    # objeto prompt y se pasa al llm y al invocarlo se le pasan las variables que se deben
    # reemplazar en el texto.
    
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
    
    # Se hace una limpieza a la respuesta del historiador para que se vea bien en el campo 
    # donde se recuperan los datos en la web.
    
    synthesis_text = response.content.replace("Síntesis Narrativa:", "").strip()
    
    return {"final_synthesis": synthesis_text}

# Por ultimo se definen los diferentes nodos y las aristas del grafo. Cada agente sera un
# nodo, se define el inicio como el agente "Survivor", pasa por los demas nodos agentes de
# manera lineal. Con el siguiente orden, Survivor, Speculator, Auteur, Synthestizar 
# (Historiador) y por ultimo se le da terminacion al grafo. Una vez todos los componentes
# estan definidos se compila el grafo.

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
