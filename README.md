Idea principal:

1. El Contexto y Problemática

Título: Anima Fractus: Análisis de Disonancia Cognitiva Social mediante Arquitectura Multi-Agente Distribuida en Cloud.

El Contexto: Nos situamos en la ventana crítica de Abril a Junio de 2020. El mundo está en "Pausa". No es un momento estático; es un periodo de adaptación forzada.

Abril: Choque inicial, encierro total, miedo agudo.

Mayo: Adaptación, búsqueda de escape (digital/financiero).

Junio: Fatiga pandémica, "nueva normalidad", reactivación de esperanza y codicia.

La Problemática: Los modelos actuales de GenAI y análisis de datos suelen ser monolíticos. Si preguntas "¿Cómo estaba el mundo?", te dan una respuesta promediada que aplana la realidad. El problema es que la realidad social es disonante: mientras un sector de la población teme por su vida (Salud), otro ve la mayor oportunidad financiera de la década (Crypto), y otro se refugia en el arte y la introspección (Cultura/Kojima). Sin una arquitectura que separe y luego sintetice estas visiones, es imposible entender la complejidad de la psiquis humana durante una crisis.

La Solución: Una aplicación distribuida en AWS que emplea LangGraph para orquestar un debate entre tres agentes con "Weltanschauung" (visiones del mundo) radicalmente opuestas. El sistema no solo recupera datos, sino que simula la fricción entre la supervivencia, la codicia y la filosofía a lo largo del tiempo.

2. Flujo de Componentes (La Arquitectura Viva)
Así se ve el proceso cuando un usuario interactúa con tu sistema distribuido:

Capa de Presentación (EC2 Web - Flask/Streamlit):

El usuario introduce: "¿Cómo cambió la percepción de la esperanza entre el inicio del encierro en abril y el cansancio de junio?"

Esta capa envía el JSON a la capa lógica.

Capa Lógica (EC2 App - LangGraph + MCP Host):

Recibe la pregunta.

Agente Orquestador: Desglosa la pregunta en dos hitos temporales: [Hito 1: 1-15 Abril] y [Hito 2: 1-15 Junio].

Activa a los 3 Agentes de Personalidad.

Capa de Datos (EC2 DB - ChromaDB + HuggingFace Embeddings):

Los agentes usan el protocolo MCP para llamar herramientas como get_crypto_context(date='2020-04').

ChromaDB devuelve los tweets semánticamente relevantes para "esperanza/futuro" en esas fechas.

3. Simulación de Ejecución: El Pensamiento de los Agentes
Esta es la parte central. Así es como se vería el log interno del sistema (o lo que podrías mostrar en una pestaña de "Debug" en tu web para impresionar a los evaluadores).

Pregunta del Usuario: "¿Cómo evolucionó la idea de 'futuro' de Abril a Junio?"

--- FASE 1: ANÁLISIS DEL MES DE ABRIL (El Choque) ---
🤖 AGENTE A: "THE SURVIVOR" (Data: Covid + Disasters) Contexto recuperado: Tweets sobre colapso hospitalario, falta de mascarillas, hashtags #StayHome. Pensamiento (Chain of Thought): "El usuario pregunta por el futuro. Mis datos indican que en Abril el concepto de futuro ha desaparecido. El horizonte temporal es de 24 horas. El miedo es el sentimiento dominante. Comparado con los desastres de Enero, esto es sistémico." Output Interno: "En abril, el futuro no existe. Solo existe la supervivencia inmediata. La esperanza es un lujo peligroso que lleva a descuidar la seguridad."

🤖 AGENTE B: "THE SPECULATOR" (Data: Crypto Market) Contexto recuperado: Caída masiva de Marzo recuperándose, incertidumbre en los mercados, volatilidad extrema. Pensamiento (Chain of Thought): "El miedo del Agente A es mi oportunidad. Veo gráficos en rojo que empiezan a ponerse verdes. El 'futuro' en abril es una apuesta. Quienes compren ahora serán ricos." Output Interno: "El futuro está en oferta. Mientras el mundo se esconde, el dinero inteligente se está moviendo. Abril es el punto de entrada máximo."

🤖 AGENTE C: "THE AUTEUR" (Data: Hideo Kojima) Contexto recuperado: Tweets sobre ver películas antiguas, escuchar lluvia, fotos de comida solitaria, edición de video remota. Pensamiento (Chain of Thought): "Todos están desconectados físicamente. Como en mi juego, Death Stranding. El futuro es una habitación cerrada con una pantalla." Output Interno: "El futuro se ha vuelto interior. Escucho la lluvia. Veo una película de hace 30 años. El tiempo se ha detenido, no hay futuro, solo un eterno presente conectado por cables."

--- FASE 2: ANÁLISIS DEL MES DE JUNIO (La Adaptación) ---
🤖 AGENTE A: "THE SURVIVOR" Output Interno: "Junio trae complacencia. Las cifras siguen ahí, pero la gente ha perdido el miedo agudo. El futuro ahora es una 'nueva normalidad' que me aterra porque bajamos la guardia."

🤖 AGENTE B: "THE SPECULATOR" Output Interno: "¡Confirmación! El mercado se recupera. Mis predicciones de abril eran correctas. El futuro en junio es eufórico para el capital digital. La crisis fue el mejor catalizador."

🤖 AGENTE C: "THE AUTEUR" Output Interno: "He comprado una figura nueva. Sigo editando. La soledad se ha vuelto rutina. Hemos aprendido a construir puentes sin tocarnos. El futuro es este estado híbrido."

--- FASE 3: SÍNTESIS FINAL (Node: The Synthesizer) ---
Generando respuesta final al usuario...

"Entre Abril y Junio de 2020, la percepción del futuro sufrió una bifurcación radical:

Abril (Parálisis): Fue el mes de la negación del futuro. Mientras la población general (Survivor) vivía al día por miedo biológico, y los creativos (Auteur) se refugiaban en la introspección y la nostalgia, solo el capital especulativo (Speculator) veía un futuro, aunque fuera puramente transaccional.

Junio (Aceptación Fragmentada): Para junio, la 'esperanza' regresó pero deformada. No es un retorno a la normalidad, sino una adaptación. La angustia se convirtió en rutina (Kojima), el miedo en precaución fatigada (Covid), y la incertidumbre financiera se transformó en una agresiva recuperación digital (Crypto).

Conclusión: La humanidad no recuperó su viejo futuro; construyó tres realidades paralelas para sobrevivir."

4. Salida Deseada (El Entregable)
El proyecto entrega una aplicación web simple pero potente donde:

Frontend: Ves el chat limpio.

Sidebar (Valor Agregado): Muestra en tiempo real qué herramienta está usando cada agente ("Survivor está leyendo base de datos: covid_tweets...", "Speculator está analizando: btc_prices...").

Respuesta: Texto enriquecido generado por un modelo de HuggingFace (ej. Mistral-7B-Instruct) que sintetiza el debate.
