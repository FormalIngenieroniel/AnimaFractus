import streamlit as st
import requests
import time

# --- CONFIGURACIÓN ---
# IP Privada de tu INSTANCIA B (Logic Layer)
LOGIC_HOST_IP = "172.31.70.154" 
API_URL = f"http://{LOGIC_HOST_IP}:5000/ask"

# Configuración de página
st.set_page_config(
    page_title="Project Anima Fractus",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para dar ambiente
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #c9d1d9;
    }
    .agent-box {
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 10px;
        background-color: #161b22;
        margin-bottom: 10px;
    }
    .success-text { color: #2ea043; }
    .warning-text { color: #d29922; }
    .info-text { color: #58a6ff; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (Estado del Sistema) ---
with st.sidebar:
    st.header("🔌 System Status")
    st.markdown("---")
    st.success(f"🟢 **Presentation Layer**: Online")
    
    # Verificación de conexión simple (Ping simulado)
    st.info(f"🟡 **Logic Layer**: Conectando a {LOGIC_HOST_IP}...")
    
    st.markdown("### 🤖 Active Agents")
    st.code("Survivor (Security)\nSpeculator (Finance)\nAuteur (Philosophy)", language="text")
    
    st.markdown("---")
    st.caption("Architecture: Distributed (EC2 A-B-C)")

# --- INTERFAZ PRINCIPAL ---
st.title("🧠 Project: Anima Fractus")
st.markdown("*The 2020 Archives: Multi-Agent Analysis System*")

st.divider()

# Input del usuario
query = st.text_input(
    "Ingresa tu consulta al archivo:", 
    "¿Cómo cambió la percepción del miedo entre abril y junio?"
)

if st.button("Initialize Analysis Sequence 🚀", use_container_width=True):
    
    if not query:
        st.warning("⚠️ Protocolo abortado: Ingrese una pregunta válida.")
    else:
        # Contenedor para mostrar progreso
        status_container = st.empty()
        
        try:
            # 1. Simulación visual de "Pensamiento"
            with status_container.container():
                with st.spinner("📡 Transmitiendo a Logic Layer..."):
                    time.sleep(0.5) 
                with st.spinner("🔄 Orquestando Agentes (Survivor, Speculator, Auteur)..."):
                    # AQUÍ SE HACE LA LLAMADA REAL
                    response = requests.post(API_URL, json={"question": query}, timeout=60)
            
            # 2. Procesar Respuesta
            if response.status_code == 200:
                data = response.json()
                logs = data.get("logs", [])
                synthesis = data.get("synthesis", "No synthesis provided.")
                
                status_container.success("✅ Análisis Completado.")
                
                # --- MOSTRAR LOGS (EL DEBATE) ---
                st.subheader("🧩 Agent Thought Process")
                
                col1, col2, col3 = st.columns(3)
                
                # Definir colores e iconos por agente
                agent_meta = {
                    "Survivor": {"icon": "🛡️", "color": "red"},
                    "Speculator": {"icon": "💰", "color": "gold"},
                    "Auteur": {"icon": "🎥", "color": "blue"}
                }

                # Distribuir logs en columnas
                for i, log in enumerate(logs):
                    agent_name = log['agent']
                    meta = agent_meta.get(agent_name, {"icon": "🤖", "color": "grey"})
                    
                    # Asignar columna cíclicamente
                    target_col = [col1, col2, col3][i % 3]
                    
                    with target_col:
                        st.markdown(f"### {meta['icon']} {agent_name}")
                        with st.expander("Ver pensamiento interno", expanded=True):
                            st.write(f"_{log['thought']}_")
                            if 'context_used' in log:
                                st.caption(f"📚 Fuente: {len(log['context_used'])} documentos")

                # --- MOSTRAR SÍNTESIS FINAL ---
                st.divider()
                st.subheader("⚖️ Final Synthesis (The Historian)")
                
                st.markdown(f"""
                <div style="background-color: #21262d; padding: 25px; border-radius: 10px; border-left: 5px solid #8b949e;">
                    <p style="font-size: 1.1em; line-height: 1.6;">{synthesis}</p>
                </div>
                """, unsafe_allow_html=True)

            else:
                status_container.error(f"❌ Error del servidor Lógico: {response.status_code}")
                st.write(response.text)

        except requests.exceptions.ConnectionError:
            status_container.error(f"❌ No se pudo conectar a Logic Layer en {API_URL}. ¿Está encendido el contenedor?")
        except Exception as e:
            status_container.error(f"❌ Error crítico: {str(e)}")