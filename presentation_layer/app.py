import streamlit as st
import time
import math
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Project Anima Fractus",
    page_icon="🕯️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- GESTIÓN DE ESTADOS (MOMENTOS DEL STORYBOARD) ---
# Inicializamos las variables que controlan la narrativa
if 'step' not in st.session_state:
    st.session_state.step = 1  # 1: Inicio, 2: Debate Listo
if 'selected_book' not in st.session_state:
    st.session_state.selected_book = None # Nombre del agente seleccionado
if 'book_view' not in st.session_state:
    st.session_state.book_view = 'cover' # 'cover', 'pages', 'back'
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0
if 'simulation_data' not in st.session_state:
    st.session_state.simulation_data = {}

# --- FUNCIÓN DE DATOS SIMULADOS (MOCK) ---
def generate_mock_response(query):
    """Simula la respuesta que vendría del backend RAG"""
    lorem = "En los oscuros rincones de la historia, la verdad a menudo se fragmenta. " * 5
    lorem_long = lorem + "\n\n" + lorem + "\n\n" + lorem
    
    return {
        "Survivor": {
            "text": f"Análisis de Supervivencia: Detecto inconsistencias en los registros de seguridad. {lorem_long}",
            "rag": ["Log #404: Breach detected", "Log #405: Containment failed", "Memo: Evacuation protocol"],
            "color": "#8b0000" # Rojo oscuro
        },
        "Speculator": {
            "text": f"Proyección Financiera: El costo de oportunidad sugiere una inversión en caos. {lorem_long}",
            "rag": ["Market Report Q3", "Asset Liquidation Form", "Risk Assessment 2024"],
            "color": "#d4af37" # Dorado
        },
        "Auteur": {
            "text": f"Reflexión Filosófica: ¿Es el archivo una memoria o una prisión? {lorem_long}",
            "rag": ["Diary Entry: The Void", "Manifesto of the Lost", "Critique of Pure Reason"],
            "color": "#4b0082" # Índigo
        },
        "The Historian": {
            "text": f"Síntesis del Archivo Central: La disonancia entre la seguridad y el capital revela una fractura social. {lorem_long}",
            "rag": [], # El historiador sintetiza, no busca raw data usualmente
            "color": "#2f4f4f" # Gris pizarra
        }
    }

# --- ESTILOS CSS (MAGIC) ---
st.markdown("""
    <style>
    /* FONDO DE LA BIBLIOTECA */
    .stApp {
        background-color: #1a120b;
        background-image: url("https://www.transparenttextures.com/patterns/wood-pattern.png");
        color: #dcdcdc;
    }

    /* SIDEBAR - EL PERGAMINO */
    [data-testid="stSidebar"] {
        background-color: #f4e4bc;
        background-image: url("https://www.transparenttextures.com/patterns/aged-paper.png");
        border-right: 8px solid #3e2723;
        box-shadow: 5px 0 15px rgba(0,0,0,0.5);
    }
    /* Textos en la sidebar */
    [data-testid="stSidebar"] * {
        color: #4a3b2a !important; 
        font-family: 'Courier New', monospace;
    }
    [data-testid="stSidebar"] h1 {
        font-family: 'Garamond', serif;
        font-weight: bold;
        text-align: center;
        border-bottom: 2px solid #4a3b2a;
        padding-bottom: 10px;
    }

    /* BOTÓN VERDE "COMENZAR DEBATE" */
    .stButton > button {
        background-color: #2e7d32; /* Verde bosque */
        color: white;
        font-size: 18px;
        border: 2px solid #1b5e20;
        border-radius: 5px;
        padding: 10px 20px;
        width: 100%;
        font-family: 'Garamond', serif;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .stButton > button:hover {
        background-color: #388e3c;
        transform: scale(1.02);
    }

    /* ESTILO DE PÁGINA DE LIBRO (MOMENTO 4) */
    .book-page {
        background-color: #fffbf0;
        color: #2c2c2c;
        padding: 40px;
        font-family: 'Garamond', serif;
        font-size: 20px;
        line-height: 1.6;
        border-radius: 2px 10px 10px 2px;
        box-shadow: inset 10px 0 20px rgba(0,0,0,0.1);
        min-height: 500px;
        border: 1px solid #d7ccc8;
    }
    .rag-note {
        font-family: 'Courier New', monospace;
        background-color: #eceff1;
        padding: 10px;
        border-left: 4px solid #b71c1c;
        font-size: 14px;
        margin-bottom: 20px;
        color: #333;
    }
    
    /* BOTÓN INVISIBLE PARA FONDO (TRUCO) */
    .overlay-close-btn {
        width: 100%;
        height: 100vh;
        background: transparent;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 998;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR: SYSTEM SCROLL (MOMENTO 1) ---
with st.sidebar:
    st.title("📜 System Scroll")
    st.markdown("**Status del Archivo**")
    st.write("---")
    st.markdown("✅ **Conexión**: Estable")
    st.markdown("🧠 **Memoria**: 84%")
    st.markdown("⚠️ **Disonancia**: Baja")
    st.write("---")
    st.markdown("### Agentes Activos:")
    st.code("Survivor\nSpeculator\nAuteur\nHistorian", language="text")

# --- LÓGICA PRINCIPAL ---

# Si hay un libro seleccionado, entramos en MODO LECTURA (Momentos 3, 4, 5)
if st.session_state.selected_book:
    
    # Fondo negro con transparencia (Overlay)
    st.markdown("""
        <div style='position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
        background-color: rgba(0,0,0,0.85); z-index: 0; pointer-events: none;'></div>
    """, unsafe_allow_html=True)

    # Botón para salir (Click en el fondo)
    col_exit = st.columns([1])[0]
    if col_exit.button("❌ Cerrar Libro (Click para salir)", key="exit_btn"):
        st.session_state.selected_book = None
        st.session_state.book_view = 'cover'
        st.session_state.current_page = 0
        st.rerun()

    # Contenedor central del libro
    c1, c2, c3 = st.columns([1, 6, 1])
    
    agent_data = st.session_state.simulation_data[st.session_state.selected_book]
    full_text = agent_data['text']
    
    # Calcular páginas (aprox 600 caracteres por página)
    chars_per_page = 600
    total_pages = math.ceil(len(full_text) / chars_per_page)

    with c2:
        # --- MOMENTO 3: PORTADA ---
        if st.session_state.book_view == 'cover':
            # Imagen de portada
            st.image(f"imágenes/libro_{st.session_state.selected_book.lower()}_portada.jpg", 
                     caption=f"Registro de: {st.session_state.selected_book}", use_container_width=True)
            
            # Flecha Roja a la derecha
            col_spacer, col_arrow = st.columns([5, 1])
            with col_arrow:
                if st.button("➡️", key="open_book"):
                    st.session_state.book_view = 'pages'
                    st.rerun()

        # --- MOMENTO 4: PÁGINAS (CONTENIDO) ---
        elif st.session_state.book_view == 'pages':
            
            # Texto de la página actual
            start = st.session_state.current_page * chars_per_page
            end = start + chars_per_page
            page_content = full_text[start:end]
            
            # Construir HTML de la página
            rag_html = ""
            # Mostrar RAG solo en la primera página
            if st.session_state.current_page == 0 and agent_data['rag']:
                rag_list = "".join([f"<li>{r}</li>" for r in agent_data['rag']])
                rag_html = f"<div class='rag-note'><strong>📎 Fuentes Recuperadas:</strong><ul>{rag_list}</ul></div>"
            
            st.markdown(f"""
                <div class="book-page">
                    {rag_html}
                    <p>{page_content}</p>
                    <div style="text-align: center; margin-top: 50px; color: #888;">
                        - {st.session_state.current_page + 1} / {total_pages} -
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Navegación (Flechas Izquierda y Derecha)
            nav_c1, nav_c2, nav_c3 = st.columns([1, 4, 1])
            
            with nav_c1:
                if st.button("⬅️", key="prev_page"):
                    if st.session_state.current_page > 0:
                        st.session_state.current_page -= 1
                    else:
                        st.session_state.book_view = 'cover'
                    st.rerun()
            
            with nav_c3:
                if st.button("➡️", key="next_page"):
                    if st.session_state.current_page < total_pages - 1:
                        st.session_state.current_page += 1
                    else:
                        st.session_state.book_view = 'back'
                    st.rerun()

        # --- MOMENTO 5: CONTRAPORTADA ---
        elif st.session_state.book_view == 'back':
            st.image(f"imágenes/libro_{st.session_state.selected_book.lower()}_contraportada.jpg", use_container_width=True)
            
            # Flecha Roja a la izquierda (Volver a abrir)
            col_arrow, col_spacer = st.columns([1, 5])
            with col_arrow:
                if st.button("⬅️", key="reopen_book"):
                    st.session_state.book_view = 'pages'
                    st.session_state.current_page = total_pages - 1
                    st.rerun()

# --- MODO LIBRERÍA (MOMENTOS 1 Y 2) ---
else:
    # Título y Descripción
    st.title("🏛️ Biblioteca de la Disonancia")
    st.markdown("*Archivo Central de Inteligencia Artificial*")
    
    # Barra de búsqueda
    query = st.text_input("Ingresa tu consulta al archivo:", "¿Cuál es el costo del miedo?")
    
    # Botón "Comenzar Debate" (Reemplaza al initialize analysis)
    if st.button("Comenzar debate"):
        if query:
            with st.spinner("Los agentes están escribiendo sus libros..."):
                time.sleep(2) # Simular proceso RAG
                st.session_state.simulation_data = generate_mock_response(query)
                st.session_state.step = 2
                st.rerun()
    
    st.divider()

    # Layout de la Biblioteca
    col_lib, col_char = st.columns([3, 1])
    
    with col_lib:
        # MOMENTO 1: Librería Vacía
        if st.session_state.step == 1:
            st.image("imágenes/fondo_libreria.jpg", caption="Esperando consulta...", use_container_width=True)
        
        # MOMENTO 2: Librería con Libros (Clickeables)
        elif st.session_state.step == 2:
            st.markdown("### 📖 Selecciona un registro para leer:")
            
            # Usamos columnas para posicionar los 4 libros "encima" de la estantería
            b1, b2, b3, b4 = st.columns(4)
            
            with b1:
                st.image("imágenes/libro_survivor_en_biblioteca.jpg", use_container_width=True)
                if st.button("Leer Survivor"):
                    st.session_state.selected_book = "Survivor"
                    st.rerun()
            
            with b2:
                st.image("imágenes/libro_speculator_en_biblioteca.jpg", use_container_width=True)
                if st.button("Leer Speculator"):
                    st.session_state.selected_book = "Speculator"
                    st.rerun()
            
            with b3:
                st.image("imágenes/libro_auteur_en_biblioteca.jpg", use_container_width=True)
                if st.button("Leer Auteur"):
                    st.session_state.selected_book = "Auteur"
                    st.rerun()
            
            with b4:
                st.image("imágenes/libro_historian_en_biblioteca.jpg", use_container_width=True)
                if st.button("Leer Historian"):
                    st.session_state.selected_book = "The Historian"
                    st.rerun()

    with col_char:
        # El personaje con el globo de texto (siempre visible)
        st.image("imágenes/personaje_explicacion.png", use_container_width=True)