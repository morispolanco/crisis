import streamlit as st
import requests # Use requests library
import json
import time
import random
import os # Potentially useful, though Streamlit secrets are preferred

# --- Configuration ---
# Use the model from the curl example or choose another appropriate one
# Common options: gemini-1.5-flash-latest, gemini-1.5-pro-latest, gemini-pro
MODEL_NAME = "gemini-1.5-flash-latest"
API_ENDPOINT_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_TIMEOUT = 120 # Seconds for API requests

# --- API Key Loading ---
GEMINI_API_KEY = None
GEMINI_AVAILABLE = False
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    if not GEMINI_API_KEY:
        raise KeyError("GEMINI_API_KEY secret is empty.")
    GEMINI_AVAILABLE = True
    st.sidebar.success(f"✅ Clave API Cargada ({MODEL_NAME})")
except KeyError:
    st.error("""
        ⚠️ **Error: Clave API de Gemini no encontrada.**
        - Asegúrate de que tu clave API está guardada en los secretos de Streamlit como `GEMINI_API_KEY`.
        - La funcionalidad de IA está deshabilitada.
        """)
except Exception as e:
     st.error(f"⚠️ Error inesperado al cargar la clave API: {e}")

# --- Helper Function for API Calls ---

def make_gemini_request(prompt, api_key, model=MODEL_NAME, timeout=DEFAULT_TIMEOUT):
    """Sends a prompt to the Gemini API via HTTP POST and returns the generated text."""
    if not GEMINI_AVAILABLE or not api_key:
        st.error("Intento de llamada a Gemini API sin clave válida.")
        return None

    url = f"{API_ENDPOINT_BASE}/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        # Optional: Add safety settings or generation config if needed
        # "safetySettings": [...],
        # "generationConfig": { "temperature": 0.7, "maxOutputTokens": 8192 }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=timeout)
        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)

        response_json = response.json()

        # Navigate the response structure to get the text
        # Check for candidates and parts وجودهم قبل الوصول إليهم
        if (candidates := response_json.get("candidates")) and \
           isinstance(candidates, list) and len(candidates) > 0 and \
           (content := candidates[0].get("content")) and \
           isinstance(content, dict) and \
           (parts := content.get("parts")) and \
           isinstance(parts, list) and len(parts) > 0 and \
           (text := parts[0].get("text")):
            return text
        else:
            st.error("❌ Respuesta de Gemini recibida, pero la estructura JSON es inesperada o no contiene texto.")
            st.json(response_json) # Show the unexpected structure
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error de Red/Conexión al llamar a Gemini API: {e}")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Error HTTP {e.response.status_code} de Gemini API: {e.response.text}")
        return None
    except json.JSONDecodeError as e:
         st.error(f"❌ Error al decodificar la respuesta JSON principal de Gemini API: {e}")
         st.text(f"Respuesta recibida (no JSON): {response.text}")
         return None
    except Exception as e:
        st.error(f"❌ Error inesperado durante la llamada a Gemini API: {e}")
        return None

# --- Helper Function to Parse Expected JSON Content --- (Unchanged)
def parse_gemini_json_response(response_text):
    """Intenta parsear JSON de la respuesta de Gemini, limpiando posibles decoradores."""
    if not response_text: return None
    try:
        # Gemini a veces envuelve el JSON en ```json ... ```
        text_to_parse = response_text.strip()
        if text_to_parse.startswith("```json"):
            text_to_parse = text_to_parse[7:-3].strip() # Quita ```json y ```
        elif text_to_parse.startswith("```"):
             text_to_parse = text_to_parse[3:-3].strip() # Quita ```
        return json.loads(text_to_parse)
    except json.JSONDecodeError as e:
        st.error(f"❌ Error al decodificar el contenido JSON esperado de Gemini: {e}")
        st.text_area("Contenido recibido (no es el JSON esperado):", response_text, height=150)
        return None
    except Exception as e:
        st.error(f"❌ Error inesperado al procesar contenido JSON de Gemini: {e}")
        st.text_area("Contenido recibido:", response_text, height=150)
        return None

# --- Funciones Adaptadas para Usar `requests` ---

def generar_escenario_gemini(nivel):
    """ Genera 5 escenarios únicos para el nivel dado usando Gemini via HTTP """
    prompt = f"""
    Eres un experto en ética empresarial y diseño de simulaciones interactivas.
    Genera EXACTAMENTE 5 escenarios únicos y distintos de crisis empresariales en español para un nivel de dificultad '{nivel}'.
    Cada escenario debe incluir:
    - 'id': Un identificador único y corto (ej: 'p1', 'p2' para principiante; 'i1', 'i2' para intermedio; 'a1', 'a2' para avanzado). Usa el prefijo correcto para el nivel ({nivel[0].lower()}).
    - 'titulo': Un título corto, atractivo y descriptivo en español (máx 10 palabras).
    - 'trasfondo': Una descripción detallada (100-150 palabras) de la empresa ficticia, el contexto del mercado, el inicio de la crisis y el rol específico que asume el jugador en la simulación. Debe estar en español.
    - 'estado_inicial': Un diccionario fijo: {{"financiera": 0, "reputacion": 0, "laboral": 0}}.

    Asegúrate de que los escenarios sean apropiados para la dificultad indicada (Principiante: dilemas directos; Intermedio: ambigüedad, pros/contras; Avanzado: sistémico, multi-agente, largo plazo).

    Presenta la respuesta final EXCLUSIVAMENTE como una lista JSON válida de estos 5 diccionarios. No incluyas ningún otro texto antes o después de la lista JSON.
    """
    with st.spinner(f"🧠 Generando escenarios ({nivel})..."):
        generated_text = make_gemini_request(prompt, GEMINI_API_KEY)
        if not generated_text:
            return [] # Error manejado en make_gemini_request

        parsed_response = parse_gemini_json_response(generated_text)

        # Resto de la validación (igual que antes)
        if parsed_response and isinstance(parsed_response, list) and len(parsed_response) == 5:
                validated_scenarios = []
                for i, sc in enumerate(parsed_response):
                    if isinstance(sc, dict) and all(k in sc for k in ['id', 'titulo', 'trasfondo', 'estado_inicial']):
                        # Asegurar IDs únicos si Gemini falla
                        if 'id' not in sc or not sc['id']:
                                sc['id'] = f"{nivel[0].lower()}{i+1}_{random.randint(1000,9999)}"
                        # Asegurar que el ID empiece con la letra correcta
                        if not sc['id'].startswith(nivel[0].lower()):
                            sc['id'] = f"{nivel[0].lower()}{sc['id'].lstrip('pia')}" # Intenta corregir prefijo

                        if not isinstance(sc['estado_inicial'], dict) or not all(k in sc['estado_inicial'] for k in ['financiera', 'reputacion', 'laboral']):
                                sc['estado_inicial'] = {"financiera": 0, "reputacion": 0, "laboral": 0} # Corregir si es necesario
                        validated_scenarios.append(sc)
                    else:
                        st.warning(f"Escenario {i+1} recibido de Gemini no tiene el formato esperado. Omitiendo.")
                if len(validated_scenarios) == 5:
                    st.success(f"✅ ¡5 escenarios ({nivel}) generados!")
                    return validated_scenarios
                else:
                    st.error(f"Error: Se esperaban 5 escenarios válidos, pero se obtuvieron {len(validated_scenarios)}. Verifica el prompt y la respuesta de Gemini.")
                    return []
        elif parsed_response:
                st.error(f"Error: Se esperaba una lista de 5 elementos, pero se recibió otra estructura.")
                st.json(parsed_response)
                return []
        else:
                # Error ya mostrado por parse_gemini_json_response
                return []

def generar_pregunta_y_opciones_gemini(contexto, historial, estado, nivel, numero_pregunta):
    """ Genera la siguiente pregunta y opciones usando Gemini via HTTP """
    historial_str = json.dumps(historial[-2:], ensure_ascii=False) # Últimas 2 decisiones

    prompt = f"""
    Actúa como el director experto de una simulación interactiva de crisis empresarial en español.
    Nivel: {nivel}. Pregunta: {numero_pregunta}/10. Estado: Fin={estado['financiera']}, Rep={estado['reputacion']}, Lab={estado['laboral']}.
    Contexto: {contexto}
    Historial reciente: {historial_str}

    Genera la SIGUIENTE pregunta crítica (concisa, relevante, dilema claro) y EXACTAMENTE 4 opciones de respuesta (distintas, plausibles, prefijo A/B/C/D).

    Presenta la respuesta final EXCLUSIVAMENTE como un objeto JSON válido con claves 'pregunta' (string) y 'opciones' (lista de 4 strings). No incluyas texto adicional.
    """
    with st.spinner(f"🧠 Generando pregunta {numero_pregunta}..."):
        generated_text = make_gemini_request(prompt, GEMINI_API_KEY)
        if not generated_text:
            return "Pregunta no disponible (Error API)", []

        parsed_response = parse_gemini_json_response(generated_text)

        if parsed_response and isinstance(parsed_response, dict) and \
           'pregunta' in parsed_response and 'opciones' in parsed_response and \
           isinstance(parsed_response['opciones'], list) and len(parsed_response['opciones']) == 4:
            # Validar prefijos A) B) C) D) si es necesario
            return parsed_response['pregunta'], parsed_response['opciones']
        else:
            st.error("Error: Formato inesperado para pregunta/opciones.")
            if parsed_response: st.json(parsed_response)
            return f"Error al generar pregunta {numero_pregunta}. ¿Continuar?", ["A) Sí", "B) No", "C) Intentar de nuevo", "D) Salir"]


def evaluar_decision_gemini(contexto, pregunta, opcion_elegida, estado_actual, nivel, numero_pregunta):
    """ Evalúa la decisión, genera análisis/consecuencias y nuevo contexto via HTTP """
    prompt = f"""
    Eres un analista experto evaluando una decisión en una simulación en español.
    Nivel: {nivel}. Pregunta respondida: {numero_pregunta}/10.
    Contexto ANTES: {contexto}
    Pregunta: {pregunta}
    Decisión: {opcion_elegida}
    Estado ANTES: Fin={estado_actual['financiera']}, Rep={estado_actual['reputacion']}, Lab={estado_actual['laboral']}.

    Realiza estas tareas y presenta el resultado EXCLUSIVAMENTE como un único objeto JSON válido con claves 'analisis', 'consecuencias_texto', 'impacto', 'nuevo_contexto':
    1.  'analisis': Análisis conciso (2-3 frases) de la decisión (implicaciones éticas/estratégicas).
    2.  'consecuencias_texto': Descripción breve (1-2 frases) de efectos inmediatos probables.
    3.  'impacto': Diccionario JSON con impacto numérico MÁS PROBABLE en 'financiera', 'reputacion', 'laboral' (enteros, rango -3 a +3 típico). E.g., {{"financiera": -1, "reputacion": 0, "laboral": -1}}.
    4.  'nuevo_contexto': Nuevo párrafo de contexto (50-100 palabras) describiendo la situación DESPUÉS de la decisión y consecuencias.

    No incluyas texto adicional fuera del objeto JSON.
    """
    with st.spinner(f"🧠 Analizando decisión {numero_pregunta}..."):
         # Usar un timeout más largo para evaluación si es necesario
        generated_text = make_gemini_request(prompt, GEMINI_API_KEY, timeout=150)
        if not generated_text:
            return "Análisis no disponible (error API).", "Consecuencias no disponibles (error API).", f"{contexto}\n\n(Error al procesar la última decisión).", {"financiera": 0, "reputacion": 0, "laboral": 0}

        parsed_response = parse_gemini_json_response(generated_text)

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
            st.error("Error: Formato inesperado para la evaluación.")
            if parsed_response: st.json(parsed_response)
            return "Análisis no disponible (error formato).", "Consecuencias no disponibles (error formato).", f"{contexto}\n\n(Error al procesar la última decisión).", {"financiera": 0, "reputacion": 0, "laboral": 0}


# --- Lógica de la Aplicación Streamlit ---
# (El resto del código de app.py: inicializar_estado, lógica de páginas Inicio,
# Simulación, Resultado) se mantiene prácticamente igual que en la respuesta
# anterior donde ya se usaban las funciones _gemini.
# Asegúrate de copiar esa parte del código aquí.)

# ... (Pegar aquí toda la lógica de Streamlit desde inicializar_estado() hasta el final del archivo app.py de la respuesta anterior) ...
# ... (Incluyendo las secciones: --- Inicialización del estado ---, --- Barra Lateral ---, --- Lógica de Páginas --- [Inicio, Simulación, Resultado])

# Ejemplo de cómo debería continuar (copia el bloque completo de la respuesta anterior):
# --- Inicialización del estado de sesión si no existe ---
def inicializar_estado():
    if 'pagina_actual' not in st.session_state:
        st.session_state.pagina_actual = 'inicio'
    if 'nivel_dificultad' not in st.session_state:
        st.session_state.nivel_dificultad = "Principiante"
    if 'cache_escenarios' not in st.session_state:
        st.session_state.cache_escenarios = {}
    # ... resto de inicializar_estado ...

inicializar_estado()

# --- Barra Lateral de Navegación ---
st.sidebar.title("Navegación")
st.sidebar.page_link("app.py", label="Inicio / Simulación")
st.sidebar.page_link("pages/acerca_de.py", label="Acerca de")
st.sidebar.page_link("pages/contacto.py", label="Contacto")
# (El estado de la API ya se muestra al inicio)

# --- Lógica de Páginas ---
# Página de Inicio
if st.session_state.pagina_actual == 'inicio':
    # ... (Código de la página de inicio igual que antes) ...
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
             st.session_state.cache_escenarios[nivel] = generar_escenario_gemini(nivel) # LLAMA A LA NUEVA FUNCIÓN
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
        opciones_escenario = {esc.get('id', f'missing_id_{i}'): esc.get('titulo', f'Sin Título {i}') for i, esc in enumerate(escenarios_disponibles)}
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
            st.session_state.datos_escenario = next((esc for esc in escenarios_disponibles if esc.get('id') == escenario_id), None)

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


                # Generar la primera pregunta (LLAMA A LA NUEVA FUNCIÓN)
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
    # ... (Código de la página de simulación igual que antes,
    #      asegúrate que llame a las NUEVAS funciones _gemini
    #      para generar preguntas y evaluar decisiones) ...

    if not st.session_state.datos_escenario:
        # ... (manejo de error) ...
        st.error("Error: No se ha cargado ningún escenario. Volviendo al inicio.")
        st.session_state.pagina_actual = 'inicio'
        time.sleep(2)
        st.rerun()


    # Asegurarse de que haya una pregunta cargada, si no, intentar generar la inicial
    elif not st.session_state.pregunta_actual and st.session_state.numero_pregunta == 1:
         # ... (regenerar primera pregunta) ...
         st.warning("Recargando primera pregunta...")
         pregunta, opciones = generar_pregunta_y_opciones_gemini( # LLAMA A LA NUEVA FUNCIÓN
                    st.session_state.contexto_actual,
                    st.session_state.historial_decisiones,
                    st.session_state.estado_simulacion,
                    st.session_state.nivel_dificultad,
                    1
                )
         # ... (resto de la lógica) ...
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
        # ... (Mostrar métricas, progreso, análisis anterior) ...
        col1, col2, col3 = st.columns(3)
        delta_fin = st.session_state.estado_simulacion.get('financiera',0) - st.session_state.estado_anterior.get('financiera',0)
        delta_rep = st.session_state.estado_simulacion.get('reputacion',0) - st.session_state.estado_anterior.get('reputacion',0)
        delta_lab = st.session_state.estado_simulacion.get('laboral',0) - st.session_state.estado_anterior.get('laboral',0)
        col1.metric("💰 Situación Financiera", st.session_state.estado_simulacion.get('financiera',0), delta=f"{delta_fin:+}" if delta_fin else None)
        col2.metric("📈 Reputación", st.session_state.estado_simulacion.get('reputacion',0), delta=f"{delta_rep:+}" if delta_rep else None)
        col3.metric("👥 Clima Laboral", st.session_state.estado_simulacion.get('laboral',0), delta=f"{delta_lab:+}" if delta_lab else None)
        progress_value = min(st.session_state.numero_pregunta / 10, 1.0)
        st.progress(progress_value)
        st.markdown(f"Pregunta {st.session_state.numero_pregunta} de 10")
        st.markdown("---")
        if st.session_state.ultimo_analisis:
             with st.expander("Análisis de tu Decisión Anterior", expanded=False):
                 st.subheader("Análisis:")
                 st.info(st.session_state.ultimo_analisis)
                 st.subheader("Consecuencias:")
                 st.warning(st.session_state.ultimas_consecuencias)
        st.subheader("Situación Actual:")
        st.markdown(st.session_state.contexto_actual)
        st.markdown("---")
        st.subheader(f"Pregunta {st.session_state.numero_pregunta}:")
        st.markdown(st.session_state.pregunta_actual if st.session_state.pregunta_actual else "Cargando pregunta...")

        # ... (Mostrar pregunta y opciones radio) ...
        if st.session_state.opciones_actuales:
            user_choice = st.radio("Selecciona tu decisión:",
                                   st.session_state.opciones_actuales,
                                   index=None,
                                   key=f"q_{st.session_state.numero_pregunta}")
        else:
             st.warning("Cargando opciones...")
             user_choice = None

        # ... (Botón Confirmar Decisión y lógica de procesamiento) ...
        if st.button("Confirmar Decisión", key=f"b_{st.session_state.numero_pregunta}", disabled=(not user_choice)):
            if user_choice:
                st.session_state.estado_anterior = st.session_state.estado_simulacion.copy()
                st.session_state.historial_decisiones.append({"pregunta": st.session_state.pregunta_actual, "respuesta": user_choice, "numero": st.session_state.numero_pregunta})

                # Evaluar decisión (LLAMA A LA NUEVA FUNCIÓN)
                analisis, cons_texto, nuevo_contexto, impacto = evaluar_decision_gemini(
                    st.session_state.contexto_actual,
                    st.session_state.pregunta_actual,
                    user_choice,
                    st.session_state.estado_simulacion,
                    st.session_state.nivel_dificultad,
                    st.session_state.numero_pregunta
                )

                # ... (Actualizar estado, contexto, análisis, consecuencias) ...
                if isinstance(impacto, dict):
                    st.session_state.estado_simulacion['financiera'] = st.session_state.estado_simulacion.get('financiera',0) + impacto.get('financiera', 0)
                    st.session_state.estado_simulacion['reputacion'] = st.session_state.estado_simulacion.get('reputacion',0) + impacto.get('reputacion', 0)
                    st.session_state.estado_simulacion['laboral'] = st.session_state.estado_simulacion.get('laboral',0) + impacto.get('laboral', 0)
                else:
                     st.error("Error: El impacto recibido de Gemini no es válido. El estado no cambiará.")
                st.session_state.contexto_actual = nuevo_contexto if nuevo_contexto else st.session_state.contexto_actual
                st.session_state.ultimo_analisis = analisis
                st.session_state.ultimas_consecuencias = cons_texto
                st.session_state.pregunta_actual = ""
                st.session_state.opciones_actuales = []


                # ... (Verificar condiciones de fin) ...
                BANCARROTA_THRESHOLD = -10
                if st.session_state.numero_pregunta >= 10:
                    st.session_state.juego_terminado = True
                    st.session_state.razon_fin = "Se completaron las 10 preguntas."
                elif st.session_state.estado_simulacion.get('financiera', 0) <= BANCARROTA_THRESHOLD:
                     st.session_state.juego_terminado = True
                     st.session_state.razon_fin = f"¡Bancarrota! La situación financiera cayó a {st.session_state.estado_simulacion.get('financiera', 0)} (Umbral: {BANCARROTA_THRESHOLD})."

                # ... (Si no termina, generar siguiente pregunta) ...
                if st.session_state.juego_terminado:
                    # ... (calcular puntaje, ir a resultados) ...
                    st.session_state.puntaje_final = (
                        st.session_state.estado_simulacion.get('financiera', 0) +
                        st.session_state.estado_simulacion.get('reputacion', 0) +
                        st.session_state.estado_simulacion.get('laboral', 0)
                    )
                    st.session_state.pagina_actual = 'resultado'
                    st.rerun()

                else:
                    st.session_state.numero_pregunta += 1
                    pregunta, opciones = generar_pregunta_y_opciones_gemini( # LLAMA A LA NUEVA FUNCIÓN
                        st.session_state.contexto_actual,
                        st.session_state.historial_decisiones,
                        st.session_state.estado_simulacion,
                        st.session_state.nivel_dificultad,
                        st.session_state.numero_pregunta
                    )
                    # ... (manejar si falla la generación) ...
                    if pregunta and opciones:
                        st.session_state.pregunta_actual = pregunta
                        st.session_state.opciones_actuales = opciones
                    else:
                         st.error(f"No se pudo generar la pregunta {st.session_state.numero_pregunta}. Finalizando simulación.")
                         st.session_state.juego_terminado = True
                         st.session_state.razon_fin = f"Error al generar la pregunta {st.session_state.numero_pregunta}."
                         st.session_state.pagina_actual = 'resultado'

                    st.rerun()

# Página de Resultados
elif st.session_state.pagina_actual == 'resultado':
    # ... (Código de la página de resultados igual que antes) ...
    st.title("🏁 Resultados de la Simulación")
    # ... (mostrar título, razón fin, métricas finales, puntaje, historial, botón volver) ...
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
    with st.expander("Ver Historial de Decisiones"):
        for i, decision in enumerate(st.session_state.historial_decisiones):
            st.markdown(f"**P{decision.get('numero', i+1)}:** {decision.get('pregunta','-')}")
            st.caption(f"Respuesta: {decision.get('respuesta','-')}")
            st.markdown("---")
    st.markdown("---")
    if st.button("Volver al Inicio", key="back_to_start"):
        # ... (resetear estado) ...
        st.session_state.pagina_actual = 'inicio'
        st.session_state.escenario_seleccionado_id = None
        st.session_state.datos_escenario = None
        keys_to_reset = ['estado_simulacion', 'estado_anterior', 'numero_pregunta',
                         'contexto_actual', 'pregunta_actual', 'opciones_actuales',
                         'historial_decisiones', 'ultimo_analisis', 'ultimas_consecuencias',
                         'juego_terminado', 'razon_fin', 'puntaje_final']
        for key in keys_to_reset:
            if key in st.session_state:
                del st.session_state[key]
        inicializar_estado()
        st.rerun()
