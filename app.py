import streamlit as st
import google.generativeai as genai
import json # Para parsear las respuestas JSON de Gemini
import time # Para pausas cortas si es necesario
import random # Para generar IDs únicos si Gemini no los proporciona consistentemente

# --- Configuración Inicial y Carga de API Key ---
GEMINI_AVAILABLE = False
model = None
try:
    # Carga la clave API desde los secretos de Streamlit
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
    # Inicializa el modelo (ajusta 'gemini-pro' si usas otro o uno más reciente como gemini-1.5-flash)
    model = genai.GenerativeModel('gemini-pro')
    # Verificar que el modelo se inicializó (podría fallar con clave inválida)
    # Intenta una llamada corta o verifica algún atributo si es posible
    # model.generate_content("test", generation_config=genai.types.GenerationConfig(max_output_tokens=5)) # Opcional: llamada de prueba
    GEMINI_AVAILABLE = True
    st.sidebar.success("✅ API de Gemini Conectada")

except (KeyError, AttributeError, Exception) as e:
    st.error(f"""
        ⚠️ **Error al configurar la API de Gemini:**
        - Asegúrate de que tu clave API está guardada en los secretos de Streamlit como `GEMINI_API_KEY`.
        - Verifica que la clave API sea válida y tenga permisos.
        - Error Detallado: `{e}`
        **La funcionalidad de IA está deshabilitada.** Se usarán datos de respaldo limitados o la app podría no funcionar.
        """)
    GEMINI_AVAILABLE = False

# --- Funciones Reales de Gemini ---

def parse_gemini_json_response(response_text):
    """Intenta parsear JSON de la respuesta de Gemini, limpiando posibles decoradores."""
    try:
        # Gemini a veces envuelve el JSON en ```json ... ```
        if response_text.strip().startswith("```json"):
            response_text = response_text.strip()[7:-3].strip() # Quita ```json y ```
        elif response_text.strip().startswith("```"):
             response_text = response_text.strip()[3:-3].strip() # Quita ```
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        st.error(f"❌ Error al decodificar JSON de Gemini: {e}")
        st.text_area("Respuesta recibida (no JSON válido):", response_text, height=150)
        return None
    except Exception as e:
        st.error(f"❌ Error inesperado al procesar respuesta de Gemini: {e}")
        st.text_area("Respuesta recibida:", response_text, height=150)
        return None


def generar_escenario_gemini(nivel):
    """ Genera 5 escenarios únicos para el nivel dado usando Gemini """
    if not GEMINI_AVAILABLE or not model:
        st.error("API de Gemini no disponible. No se pueden generar escenarios.")
        return [] # Devuelve lista vacía si no hay API

    prompt = f"""
    Eres un experto en ética empresarial y diseño de simulaciones interactivas.
    Genera EXACTAMENTE 5 escenarios únicos y distintos de crisis empresariales en español para un nivel de dificultad '{nivel}'.
    Cada escenario debe incluir:
    - 'id': Un identificador único y corto (ej: 'p1', 'p2' para principiante; 'i1', 'i2' para intermedio; 'a1', 'a2' para avanzado). Usa el prefijo correcto para el nivel.
    - 'titulo': Un título corto, atractivo y descriptivo en español (máx 10 palabras).
    - 'trasfondo': Una descripción detallada (100-150 palabras) de la empresa ficticia, el contexto del mercado, el inicio de la crisis y el rol específico que asume el jugador en la simulación. Debe estar en español.
    - 'estado_inicial': Un diccionario fijo: {{"financiera": 0, "reputacion": 0, "laboral": 0}}.

    Asegúrate de que los escenarios sean apropiados para la dificultad indicada:
    - Principiante: Dilemas éticos más directos, menos variables interconectadas.
    - Intermedio: Situaciones con más ambigüedad, impacto en múltiples áreas, decisiones con pros y contras más balanceados.
    - Avanzado: Escenarios complejos, sistémicos, con múltiples partes interesadas (multi-agente), consecuencias a largo plazo y posibles efectos cascada.

    Presenta la respuesta final EXCLUSIVAMENTE como una lista JSON válida de estos 5 diccionarios. No incluyas ningún otro texto antes o después de la lista JSON.
    Ejemplo de formato de un elemento de la lista:
    {{
        "id": "p1",
        "titulo": "El Informe de Gastos Dudoso",
        "trasfondo": "Eres un nuevo empleado en TecnoSoluciones...",
        "estado_inicial": {{"financiera": 0, "reputacion": 0, "laboral": 0}}
    }}
    """
    try:
        with st.spinner(f"🧠 Generando escenarios ({nivel}) con Gemini..."):
            response = model.generate_content(prompt)
            # st.text(response.text) # Descomentar para depurar la respuesta cruda
            parsed_response = parse_gemini_json_response(response.text)

            if parsed_response and isinstance(parsed_response, list) and len(parsed_response) == 5:
                 # Validar estructura básica de cada escenario
                 validated_scenarios = []
                 for i, sc in enumerate(parsed_response):
                     if isinstance(sc, dict) and all(k in sc for k in ['id', 'titulo', 'trasfondo', 'estado_inicial']):
                         # Asegurar IDs únicos si Gemini falla
                         if 'id' not in sc or not sc['id']:
                              sc['id'] = f"{nivel[0].lower()}{i+1}_{random.randint(1000,9999)}"
                         if not isinstance(sc['estado_inicial'], dict) or not all(k in sc['estado_inicial'] for k in ['financiera', 'reputacion', 'laboral']):
                              sc['estado_inicial'] = {"financiera": 0, "reputacion": 0, "laboral": 0} # Corregir si es necesario
                         validated_scenarios.append(sc)
                     else:
                         st.warning(f"Escenario {i+1} recibido de Gemini no tiene el formato esperado. Omitiendo.")
                 if len(validated_scenarios) == 5:
                     st.success(f"✅ ¡5 escenarios ({nivel}) generados por Gemini!")
                     return validated_scenarios
                 else:
                      st.error(f"Error: Se esperaban 5 escenarios válidos, pero se obtuvieron {len(validated_scenarios)}. Verifica el prompt y la respuesta de Gemini.")
                      return []

            elif parsed_response:
                 st.error(f"Error: Gemini devolvió una estructura inesperada (no es una lista de 5 elementos).")
                 return []
            else:
                 # El error ya fue mostrado por parse_gemini_json_response
                 return []

    except Exception as e:
        st.error(f"❌ Falló la llamada a Gemini para generar escenarios: {e}")
        return [] # Devuelve lista vacía en caso de error

def generar_pregunta_y_opciones_gemini(contexto, historial, estado, nivel, numero_pregunta):
    """ Genera la siguiente pregunta y opciones usando Gemini """
    if not GEMINI_AVAILABLE or not model:
        st.error("API de Gemini no disponible.")
        return "Pregunta no disponible", []

    historial_str = json.dumps(historial[-2:], ensure_ascii=False) # Enviar solo las últimas 2 decisiones para brevedad

    prompt = f"""
    Actúa como el director experto de una simulación interactiva de crisis empresarial en español.
    Nivel de dificultad: {nivel}.
    Número de pregunta actual: {numero_pregunta} de 10.
    Estado actual de la compañía: Financiera={estado['financiera']}, Reputación={estado['reputacion']}, Clima Laboral={estado['laboral']}.
    Contexto actual de la crisis: {contexto}
    Decisiones recientes tomadas: {historial_str}

    Basado en TODA esta información, genera la SIGUIENTE pregunta crítica (1 sola pregunta concisa) que el jugador debe responder para avanzar en la simulación. La pregunta debe ser relevante al contexto y estado actual, y presentar un dilema ético o estratégico claro.
    Además, proporciona EXACTAMENTE 4 opciones de respuesta de opción múltiple (distintas, plausibles y con implicaciones variadas) para esa pregunta. Prefija cada opción con 'A) ', 'B) ', 'C) ', 'D) '.

    Presenta la respuesta final EXCLUSIVAMENTE como un objeto JSON válido con las claves 'pregunta' (string) y 'opciones' (una lista de 4 strings).
    Ejemplo de formato:
    {{
        "pregunta": "¿Qué acción priorizas ahora?",
        "opciones": [
            "A) Enfocarse en reparar la reputación externamente.",
            "B) Invertir en mejorar la moral interna del equipo.",
            "C) Buscar una solución financiera rápida aunque arriesgada.",
            "D) Esperar a tener más información antes de actuar."
        ]
    }}
    No incluyas ningún otro texto antes o después del objeto JSON.
    """
    try:
        with st.spinner(f"🧠 Generando pregunta {numero_pregunta} con Gemini..."):
            response = model.generate_content(prompt)
            # st.text(response.text) # Debug
            parsed_response = parse_gemini_json_response(response.text)

            if parsed_response and isinstance(parsed_response, dict) and \
               'pregunta' in parsed_response and 'opciones' in parsed_response and \
               isinstance(parsed_response['opciones'], list) and len(parsed_response['opciones']) == 4:
                return parsed_response['pregunta'], parsed_response['opciones']
            else:
                st.error("Error: Gemini devolvió una pregunta/opciones en formato inesperado.")
                # Fallback muy básico
                return f"Error al generar pregunta {numero_pregunta}. ¿Continuar?", ["A) Sí", "B) No", "C) Intentar de nuevo", "D) Salir"]

    except Exception as e:
        st.error(f"❌ Falló la llamada a Gemini para generar pregunta {numero_pregunta}: {e}")
        return f"Error al generar pregunta {numero_pregunta}. ¿Continuar?", ["A) Sí", "B) No", "C) Intentar de nuevo", "D) Salir"]


def evaluar_decision_gemini(contexto, pregunta, opcion_elegida, estado_actual, nivel, numero_pregunta):
    """ Evalúa la decisión, genera análisis/consecuencias y nuevo contexto """
    if not GEMINI_AVAILABLE or not model:
        st.error("API de Gemini no disponible.")
        return "Análisis no disponible.", "Consecuencias no disponibles.", contexto, {"financiera": 0, "reputacion": 0, "laboral": 0}

    prompt = f"""
    Eres un analista experto en ética y estrategia empresarial evaluando una decisión en una simulación interactiva en español.
    Nivel de dificultad: {nivel}.
    Número de pregunta respondida: {numero_pregunta} de 10.
    Contexto ANTES de la decisión: {contexto}
    Pregunta realizada al jugador: {pregunta}
    Opción elegida por el jugador: {opcion_elegida}
    Estado de la compañía ANTES de la decisión: Financiera={estado_actual['financiera']}, Reputación={estado_actual['reputacion']}, Clima Laboral={estado_actual['laboral']}.

    Por favor, realiza las siguientes tareas y presenta el resultado EXCLUSIVAMENTE como un único objeto JSON válido con las cuatro claves especificadas ('analisis', 'consecuencias_texto', 'impacto', 'nuevo_contexto'):

    1.  **'analisis'**: Escribe un análisis conciso (2-3 frases) en español explicando las implicaciones éticas y/o estratégicas de la decisión tomada ('{opcion_elegida}'). Considera los pros y contras inmediatos y potenciales a futuro.
    2.  **'consecuencias_texto'**: Describe brevemente (1-2 frases) en español los efectos MÁS PROBABLES e inmediatos de esta decisión en la situación general de la empresa.
    3.  **'impacto'**: Determina el impacto numérico MÁS PROBABLE de esta decisión en el estado de la compañía. Proporciona un diccionario JSON con las claves 'financiera', 'reputacion', 'laboral'. Los valores deben ser números enteros (positivos, negativos o cero). Sé realista y coherente con el análisis, el nivel de dificultad y el estado actual. Rango típico por decisión: -3 a +3. Ejemplo: {{"financiera": -1, "reputacion": 0, "laboral": -1}}. Asegúrate que las claves sean exactamente "financiera", "reputacion", "laboral".
    4.  **'nuevo_contexto'**: Escribe un nuevo párrafo de contexto (50-100 palabras) en español que describa cómo ha evolucionado la situación de la crisis DESPUÉS de la decisión tomada y sus consecuencias inmediatas. Este nuevo contexto será la base para la siguiente pregunta. Debe reflejar el impacto numérico y el análisis.

    Ejemplo de formato de respuesta JSON:
    {{
        "analisis": "Optar por la opción A prioriza las ganancias a corto plazo, pero ignora riesgos reputacionales significativos que podrían materializarse más adelante.",
        "consecuencias_texto": "La decisión genera ingresos inmediatos, pero aumenta la tensión con el equipo de desarrollo y genera preocupación en el departamento legal.",
        "impacto": {{ "financiera": 1, "reputacion": -1, "laboral": -1 }},
        "nuevo_contexto": "Tras la decisión de lanzar el producto apresuradamente, las ventas iniciales son buenas, aliviando la presión financiera. Sin embargo, empiezan a surgir informes de clientes sobre el problema de sobrecalentamiento en foros online. El equipo de soporte está sobrecargado y la moral interna decae mientras se trabaja en un parche urgente..."
    }}
    No incluyas ningún otro texto antes o después del objeto JSON.
    """
    try:
        with st.spinner(f"🧠 Analizando decisión {numero_pregunta} con Gemini..."):
            # Aumentar un poco el timeout si las evaluaciones son complejas
            generation_config = genai.types.GenerationConfig(
                # temperature=0.7 # Ajustar creatividad si es necesario
            )
            request_options = {"timeout": 120} # Timeout de 120 segundos

            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                request_options=request_options
                )
            # st.text(response.text) # Debug
            parsed_response = parse_gemini_json_response(response.text)

            if parsed_response and isinstance(parsed_response, dict) and \
               all(k in parsed_response for k in ['analisis', 'consecuencias_texto', 'impacto', 'nuevo_contexto']) and \
               isinstance(parsed_response['impacto'], dict) and \
               all(k in parsed_response['impacto'] for k in ['financiera', 'reputacion', 'laboral']):
                # Validar tipos de impacto
                impacto = parsed_response['impacto']
                impacto_validado = {
                    'financiera': int(impacto.get('financiera', 0)),
                    'reputacion': int(impacto.get('reputacion', 0)),
                    'laboral': int(impacto.get('laboral', 0))
                }
                return parsed_response['analisis'], parsed_response['consecuencias_texto'], parsed_response['nuevo_contexto'], impacto_validado
            else:
                st.error("Error: Gemini devolvió una evaluación en formato inesperado.")
                return "Análisis no disponible (error formato).", "Consecuencias no disponibles (error formato).", f"{contexto}\n\n(Error al procesar la última decisión. La situación no ha cambiado).", {"financiera": 0, "reputacion": 0, "laboral": 0}

    except Exception as e:
        st.error(f"❌ Falló la llamada a Gemini para evaluar decisión {numero_pregunta}: {e}")
        return "Análisis no disponible (error API).", "Consecuencias no disponibles (error API).", f"{contexto}\n\n(Error al procesar la última decisión. La situación no ha cambiado).", {"financiera": 0, "reputacion": 0, "laboral": 0}


# --- Lógica de la Aplicación Streamlit (SIN CAMBIOS SIGNIFICATIVOS) ---
# Mantener la lógica de inicialización, páginas, manejo de estado, etc.,
# exactamente como en la versión anterior, ya que ahora llamará a las
# funciones _gemini en lugar de las _mock.

# --- Inicialización del estado de sesión si no existe ---
def inicializar_estado():
    # ... (Exactamente la misma función inicializar_estado que antes) ...
    if 'pagina_actual' not in st.session_state:
        st.session_state.pagina_actual = 'inicio' # 'inicio', 'simulacion', 'resultado'
    if 'nivel_dificultad' not in st.session_state:
        st.session_state.nivel_dificultad = "Principiante"
    # Usar un caché simple para escenarios por nivel para evitar llamadas repetidas
    if 'cache_escenarios' not in st.session_state:
        st.session_state.cache_escenarios = {} # { 'Principiante': [], 'Intermedio': [], 'Avanzado': [] }
    if 'escenario_seleccionado_id' not in st.session_state:
        st.session_state.escenario_seleccionado_id = None
    if 'datos_escenario' not in st.session_state:
        st.session_state.datos_escenario = None # Contendrá título, trasfondo, etc.
    if 'estado_simulacion' not in st.session_state:
        st.session_state.estado_simulacion = {"financiera": 0, "reputacion": 0, "laboral": 0}
    if 'estado_anterior' not in st.session_state: # Para calcular deltas
        st.session_state.estado_anterior = {"financiera": 0, "reputacion": 0, "laboral": 0}
    if 'numero_pregunta' not in st.session_state:
        st.session_state.numero_pregunta = 0
    if 'contexto_actual' not in st.session_state:
        st.session_state.contexto_actual = ""
    if 'pregunta_actual' not in st.session_state:
        st.session_state.pregunta_actual = ""
    if 'opciones_actuales' not in st.session_state:
        st.session_state.opciones_actuales = []
    if 'historial_decisiones' not in st.session_state:
        st.session_state.historial_decisiones = []
    if 'ultimo_analisis' not in st.session_state:
        st.session_state.ultimo_analisis = ""
    if 'ultimas_consecuencias' not in st.session_state:
        st.session_state.ultimas_consecuencias = ""
    if 'juego_terminado' not in st.session_state:
        st.session_state.juego_terminado = False
    if 'razon_fin' not in st.session_state:
        st.session_state.razon_fin = ""
    if 'puntaje_final' not in st.session_state:
        st.session_state.puntaje_final = 0


inicializar_estado()

# --- Barra Lateral de Navegación ---
st.sidebar.title("Navegación")
st.sidebar.page_link("app.py", label="Inicio / Simulación")
st.sidebar.page_link("pages/acerca_de.py", label="Acerca de")
st.sidebar.page_link("pages/contacto.py", label="Contacto")

# Mostrar estado de la API en la barra lateral
# (Ya se muestra éxito o error al inicio)

# --- Lógica de Páginas ---

# Página de Inicio
if st.session_state.pagina_actual == 'inicio':
    st.title("🚀 Simulador de Crisis Empresariales")
    st.markdown("Bienvenido/a. Selecciona un nivel y un escenario para comenzar a tomar decisiones críticas.")

    nivel = st.selectbox("Selecciona el Nivel de Dificultad:",
                         ["Principiante", "Intermedio", "Avanzado"],
                         index=["Principiante", "Intermedio", "Avanzado"].index(st.session_state.nivel_dificultad),
                         key="nivel_selector")

    # Si cambia el nivel, intentar cargar escenarios desde caché o generar nuevos
    if nivel != st.session_state.nivel_dificultad:
        st.session_state.nivel_dificultad = nivel
        st.session_state.escenario_seleccionado_id = None # Resetear selección
        # Forzar la recarga/regeneración en el siguiente paso
        st.rerun()

    # Cargar/generar escenarios si no están en caché para el nivel actual
    if nivel not in st.session_state.cache_escenarios or not st.session_state.cache_escenarios[nivel]:
         if GEMINI_AVAILABLE:
             st.session_state.cache_escenarios[nivel] = generar_escenario_gemini(nivel)
         else:
             st.session_state.cache_escenarios[nivel] = [] # Vacío si no hay API

         # Si la generación falló o no hay API, mostrar mensaje
         if not st.session_state.cache_escenarios[nivel] and GEMINI_AVAILABLE:
              st.error(f"No se pudieron generar escenarios para el nivel {nivel}. Intenta recargar la página o revisa la conexión/clave API.")
         elif not GEMINI_AVAILABLE:
              st.warning(f"API de Gemini no disponible. No se pueden cargar escenarios para el nivel {nivel}.")


    # Obtener escenarios disponibles del caché
    escenarios_disponibles = st.session_state.cache_escenarios.get(nivel, [])

    if escenarios_disponibles:
        opciones_escenario = {esc['id']: esc['titulo'] for esc in escenarios_disponibles}
        # Asegurarse que el ID seleccionado previamente sigue siendo válido
        current_selection_id = st.session_state.get('escenario_seleccionado_id')
        valid_ids = list(opciones_escenario.keys())
        preselected_index = valid_ids.index(current_selection_id) if current_selection_id in valid_ids else 0

        escenario_id = st.selectbox("Selecciona un Escenario:",
                                    options=valid_ids,
                                    format_func=lambda x: opciones_escenario.get(x, "ID Desconocido"),
                                    index=preselected_index,
                                    key="escenario_selector")

        if st.button("Iniciar Simulación", key="start_button"):
            st.session_state.escenario_seleccionado_id = escenario_id
            st.session_state.datos_escenario = next((esc for esc in escenarios_disponibles if esc['id'] == escenario_id), None)

            if st.session_state.datos_escenario:
                # Resetear estado para nueva simulación
                st.session_state.estado_simulacion = st.session_state.datos_escenario.get('estado_inicial', {"financiera": 0, "reputacion": 0, "laboral": 0}).copy()
                st.session_state.estado_anterior = st.session_state.estado_simulacion.copy()
                st.session_state.numero_pregunta = 0
                st.session_state.contexto_actual = st.session_state.datos_escenario.get('trasfondo', "Contexto inicial no disponible.")
                st.session_state.historial_decisiones = []
                st.session_state.ultimo_analisis = ""
                st.session_state.ultimas_consecuencias = ""
                st.session_state.juego_terminado = False
                st.session_state.razon_fin = ""
                st.session_state.puntaje_final = 0
                st.session_state.pregunta_actual = ""
                st.session_state.opciones_actuales = []


                # Generar la primera pregunta (AHORA llama a la función Gemini real)
                pregunta, opciones = generar_pregunta_y_opciones_gemini(
                    st.session_state.contexto_actual,
                    st.session_state.historial_decisiones,
                    st.session_state.estado_simulacion,
                    st.session_state.nivel_dificultad,
                    1 # Número de pregunta inicial
                )
                if pregunta and opciones:
                    st.session_state.pregunta_actual = pregunta
                    st.session_state.opciones_actuales = opciones
                    st.session_state.numero_pregunta = 1 # Empezamos con la pregunta 1
                    st.session_state.pagina_actual = 'simulacion'
                    st.rerun()
                else:
                    st.error("No se pudo generar la primera pregunta. Intenta de nuevo.")
            else:
                st.error("Error al cargar los datos del escenario seleccionado.")
    else:
        st.warning(f"No hay escenarios disponibles o no se pudieron cargar para el nivel {nivel}.")


# Página de Simulación
elif st.session_state.pagina_actual == 'simulacion':
    if not st.session_state.datos_escenario:
        st.error("Error: No se ha cargado ningún escenario. Volviendo al inicio.")
        st.session_state.pagina_actual = 'inicio'
        time.sleep(2)
        st.rerun()

    # Asegurarse de que haya una pregunta cargada, si no, intentar generar la inicial
    elif not st.session_state.pregunta_actual and st.session_state.numero_pregunta == 1:
         st.warning("Recargando primera pregunta...")
         pregunta, opciones = generar_pregunta_y_opciones_gemini(
                    st.session_state.contexto_actual,
                    st.session_state.historial_decisiones,
                    st.session_state.estado_simulacion,
                    st.session_state.nivel_dificultad,
                    1
                )
         if pregunta and opciones:
             st.session_state.pregunta_actual = pregunta
             st.session_state.opciones_actuales = opciones
             st.rerun()
         else:
             st.error("Fallo crítico al generar la primera pregunta. Regresando al inicio.")
             st.session_state.pagina_actual = 'inicio'
             time.sleep(2)
             st.rerun()

    elif st.session_state.numero_pregunta > 0: # Estado normal de simulación
        st.title(f"Simulación: {st.session_state.datos_escenario.get('titulo', 'Sin Título')}")

        # Mostrar estado actual con deltas
        col1, col2, col3 = st.columns(3)
        delta_fin = st.session_state.estado_simulacion.get('financiera',0) - st.session_state.estado_anterior.get('financiera',0)
        delta_rep = st.session_state.estado_simulacion.get('reputacion',0) - st.session_state.estado_anterior.get('reputacion',0)
        delta_lab = st.session_state.estado_simulacion.get('laboral',0) - st.session_state.estado_anterior.get('laboral',0)

        col1.metric("💰 Situación Financiera", st.session_state.estado_simulacion.get('financiera',0), delta=f"{delta_fin:+}" if delta_fin else None)
        col2.metric("📈 Reputación", st.session_state.estado_simulacion.get('reputacion',0), delta=f"{delta_rep:+}" if delta_rep else None)
        col3.metric("👥 Clima Laboral", st.session_state.estado_simulacion.get('laboral',0), delta=f"{delta_lab:+}" if delta_lab else None)

        # Barra de progreso
        progress_value = min(st.session_state.numero_pregunta / 10, 1.0) # Asegurar que no pase de 1.0
        st.progress(progress_value)
        st.markdown(f"Pregunta {st.session_state.numero_pregunta} de 10")
        st.markdown("---")

        # Mostrar análisis anterior si existe
        if st.session_state.ultimo_analisis:
             with st.expander("Análisis de tu Decisión Anterior", expanded=False):
                 st.subheader("Análisis:")
                 st.info(st.session_state.ultimo_analisis)
                 st.subheader("Consecuencias:")
                 st.warning(st.session_state.ultimas_consecuencias)

        # Mostrar contexto actual
        st.subheader("Situación Actual:")
        st.markdown(st.session_state.contexto_actual)
        st.markdown("---")

        # Mostrar pregunta y opciones
        st.subheader(f"Pregunta {st.session_state.numero_pregunta}:")
        st.markdown(st.session_state.pregunta_actual if st.session_state.pregunta_actual else "Cargando pregunta...")

        if st.session_state.opciones_actuales:
            user_choice = st.radio("Selecciona tu decisión:",
                                   st.session_state.opciones_actuales,
                                   index=None, # No selección por defecto
                                   key=f"q_{st.session_state.numero_pregunta}")
        else:
             st.warning("Cargando opciones...")
             user_choice = None # No mostrar radio si no hay opciones

        if st.button("Confirmar Decisión", key=f"b_{st.session_state.numero_pregunta}", disabled=(not user_choice)):
            if user_choice:
                # Guardar estado anterior para deltas
                st.session_state.estado_anterior = st.session_state.estado_simulacion.copy()

                # Procesar decisión
                st.session_state.historial_decisiones.append({"pregunta": st.session_state.pregunta_actual, "respuesta": user_choice, "numero": st.session_state.numero_pregunta})

                # Evaluar decisión (AHORA llama a la función Gemini real)
                analisis, cons_texto, nuevo_contexto, impacto = evaluar_decision_gemini(
                    st.session_state.contexto_actual,
                    st.session_state.pregunta_actual,
                    user_choice,
                    st.session_state.estado_simulacion,
                    st.session_state.nivel_dificultad,
                    st.session_state.numero_pregunta
                )

                # Actualizar estado de la simulación (asegurarse que impacto es un dict)
                if isinstance(impacto, dict):
                    st.session_state.estado_simulacion['financiera'] = st.session_state.estado_simulacion.get('financiera',0) + impacto.get('financiera', 0)
                    st.session_state.estado_simulacion['reputacion'] = st.session_state.estado_simulacion.get('reputacion',0) + impacto.get('reputacion', 0)
                    st.session_state.estado_simulacion['laboral'] = st.session_state.estado_simulacion.get('laboral',0) + impacto.get('laboral', 0)
                else:
                     st.error("Error: El impacto recibido de Gemini no es válido. El estado no cambiará.")


                st.session_state.contexto_actual = nuevo_contexto if nuevo_contexto else st.session_state.contexto_actual # Mantener contexto si falla la generación
                st.session_state.ultimo_analisis = analisis
                st.session_state.ultimas_consecuencias = cons_texto

                # Limpiar pregunta/opciones actuales para forzar recarga o fin
                st.session_state.pregunta_actual = ""
                st.session_state.opciones_actuales = []

                # Verificar condiciones de fin (BANCARROTA_THRESHOLD ajustable)
                BANCARROTA_THRESHOLD = -10
                if st.session_state.numero_pregunta >= 10:
                    st.session_state.juego_terminado = True
                    st.session_state.razon_fin = "Se completaron las 10 preguntas."
                elif st.session_state.estado_simulacion.get('financiera', 0) <= BANCARROTA_THRESHOLD:
                    st.session_state.juego_terminado = True
                    st.session_state.razon_fin = f"¡Bancarrota! La situación financiera cayó a {st.session_state.estado_simulacion.get('financiera', 0)} (Umbral: {BANCARROTA_THRESHOLD})."

                if st.session_state.juego_terminado:
                    # Calcular puntaje final
                    st.session_state.puntaje_final = (
                        st.session_state.estado_simulacion.get('financiera', 0) +
                        st.session_state.estado_simulacion.get('reputacion', 0) +
                        st.session_state.estado_simulacion.get('laboral', 0)
                    )
                    st.session_state.pagina_actual = 'resultado'
                    st.rerun() # Ir a página de resultados

                else:
                    # Pasar a la siguiente pregunta
                    st.session_state.numero_pregunta += 1
                    pregunta, opciones = generar_pregunta_y_opciones_gemini(
                        st.session_state.contexto_actual,
                        st.session_state.historial_decisiones,
                        st.session_state.estado_simulacion,
                        st.session_state.nivel_dificultad,
                        st.session_state.numero_pregunta
                    )
                    if pregunta and opciones:
                        st.session_state.pregunta_actual = pregunta
                        st.session_state.opciones_actuales = opciones
                    else:
                         st.error(f"No se pudo generar la pregunta {st.session_state.numero_pregunta}. Finalizando simulación.")
                         st.session_state.juego_terminado = True
                         st.session_state.razon_fin = f"Error al generar la pregunta {st.session_state.numero_pregunta}."
                         st.session_state.pagina_actual = 'resultado'

                    st.rerun() # Actualizar la interfaz para mostrar nueva pregunta o ir a resultados

            # (No es necesario 'else' aquí porque el botón está deshabilitado si no hay user_choice)


# Página de Resultados
elif st.session_state.pagina_actual == 'resultado':
    # ... (Exactamente la misma página de resultados que antes) ...
    st.title("🏁 Resultados de la Simulación")
    st.subheader(f"Escenario: {st.session_state.datos_escenario.get('titulo', 'Desconocido')}")

    st.markdown(f"**Razón del Fin:** {st.session_state.razon_fin}")
    st.markdown("---")
    st.subheader("Estado Final de la Compañía:")

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Situación Financiera Final", st.session_state.estado_simulacion.get('financiera',0))
    col2.metric("📈 Reputación Final", st.session_state.estado_simulacion.get('reputacion',0))
    col3.metric("👥 Clima Laboral Final", st.session_state.estado_simulacion.get('laboral',0))

    st.markdown("---")
    st.subheader("Puntaje Total:")
    # Calcular puntaje aquí si no se hizo antes
    if 'puntaje_final' not in st.session_state or st.session_state.puntaje_final == 0:
         st.session_state.puntaje_final = (
                        st.session_state.estado_simulacion.get('financiera', 0) +
                        st.session_state.estado_simulacion.get('reputacion', 0) +
                        st.session_state.estado_simulacion.get('laboral', 0)
                    )

    st.metric("🏆 Puntaje Final", st.session_state.puntaje_final)
    if st.session_state.puntaje_final > 5:
        st.success("¡Excelente gestión de la crisis!")
    elif st.session_state.puntaje_final < -5:
        st.error("La gestión de la crisis tuvo resultados muy negativos.")
    else:
        st.info("La gestión de la crisis tuvo un resultado mixto o neutral.")

    # Opcional: Mostrar historial de decisiones
    with st.expander("Ver Historial de Decisiones"):
        for i, decision in enumerate(st.session_state.historial_decisiones):
            st.markdown(f"**P{decision.get('numero', i+1)}:** {decision.get('pregunta','-')}")
            st.caption(f"Respuesta: {decision.get('respuesta','-')}")
            st.markdown("---")


    st.markdown("---")
    if st.button("Volver al Inicio", key="back_to_start"):
        # Resetear estado para permitir nueva partida
        st.session_state.pagina_actual = 'inicio'
        st.session_state.escenario_seleccionado_id = None
        st.session_state.datos_escenario = None
        # Mantener caché de escenarios
        # Limpiar estado de simulación específica
        keys_to_reset = ['estado_simulacion', 'estado_anterior', 'numero_pregunta',
                         'contexto_actual', 'pregunta_actual', 'opciones_actuales',
                         'historial_decisiones', 'ultimo_analisis', 'ultimas_consecuencias',
                         'juego_terminado', 'razon_fin', 'puntaje_final']
        for key in keys_to_reset:
            if key in st.session_state:
                del st.session_state[key]
        inicializar_estado() # Reinicializar valores por defecto
        st.rerun()
