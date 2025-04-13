import streamlit as st
import google.generativeai as genai
import time # Opcional, para simular delays

# --- Configuración Inicial y Carga de API Key ---
try:
    # Carga la clave API desde los secretos de Streamlit
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
    # Inicializa el modelo (ajusta 'gemini-pro' si usas otro)
    model = genai.GenerativeModel('gemini-pro')
    GEMINI_AVAILABLE = True
except (KeyError, Exception) as e:
    # Manejo si la clave no está configurada o hay error al inicializar
    st.error("⚠️ Clave API de Gemini no encontrada o inválida. La funcionalidad de IA estará deshabilitada. Configura st.secrets['GEMINI_API_KEY'].")
    # st.error(f"Error detallado: {e}") # Descomentar para depuración
    GEMINI_AVAILABLE = False
    model = None # Asegurarse que model es None si no está disponible

# --- Funciones Mock (Simuladas) para Gemini ---
# !! REEMPLAZAR ESTAS FUNCIONES CON LLAMADAS REALES A LA API !!

def mock_generar_escenario(nivel):
    """ Simula la generación del trasfondo del escenario """
    # Escenarios predefinidos simples para demostración
    escenarios_principiante = [
        {"id": "p1", "titulo": "El Informe de Gastos Dudoso", "trasfondo": "Eres nuevo en TecnoSoluciones. Tu supervisor te pide incluir un gasto personal en el informe de viaje...", "estado_inicial": {"financiera": 0, "reputacion": 0, "laboral": 0}},
        {"id": "p2", "titulo": "Presión por Cifras", "trasfondo": "Se acerca el fin de trimestre y tu equipo no llega a la meta de ventas. Tu gerente sugiere 'inflar' ligeramente las proyecciones...", "estado_inicial": {"financiera": 0, "reputacion": 0, "laboral": 0}},
        # Añadir 3 más para principiante
    ]
    escenarios_intermedio = [
        {"id": "i1", "titulo": "Lanzamiento Apresurado", "trasfondo": "Detectas un fallo menor pero potencialmente peligroso en un producto a punto de lanzarse. Retrasarlo tiene costes financieros...", "estado_inicial": {"financiera": 0, "reputacion": 0, "laboral": 0}},
        # Añadir 4 más para intermedio
    ]
    escenarios_avanzado = [
        {"id": "a1", "titulo": "El Vertido Contaminante Oculto", "trasfondo": "Descubres que la planta ha estado contaminando un río local durante años, violando normativas. Corregirlo es caro y escandaloso...", "estado_inicial": {"financiera": 0, "reputacion": 0, "laboral": 0}},
        # Añadir 4 más para avanzado
    ]
    # Seleccionar escenarios según nivel (simplificado)
    if nivel == "Principiante":
        return escenarios_principiante[:5] # Devuelve los 5 disponibles
    elif nivel == "Intermedio":
        return escenarios_intermedio[:1] # Solo 1 para el ejemplo
    elif nivel == "Avanzado":
        return escenarios_avanzado[:1] # Solo 1 para el ejemplo
    return []

def mock_generar_pregunta_y_opciones(contexto, historial, estado, nivel):
    """ Simula la generación de la siguiente pregunta y opciones """
    # Lógica simple basada en el número de pregunta para demostración
    num_pregunta = len(historial) + 1
    if "Informe de Gastos" in contexto:
        if num_pregunta == 1:
            return ("¿Qué haces con la petición de tu supervisor?",
                    ["A) Incluyes la cena como te pidió.",
                     "B) No incluyes la cena y presentas solo gastos legítimos.",
                     "C) Hablas con RRHH sobre la petición.",
                     "D) Hablas con tu supervisor expresando tu incomodidad."])
        else:
             return (f"Pregunta {num_pregunta}: Situación derivada...", ["Opción X", "Opción Y", "Opción Z", "Opción W"])
    elif "Lanzamiento Apresurado" in contexto:
         if num_pregunta == 1:
             return ("¿Cuál es tu recomendación sobre el lanzamiento?",
                     ["A) Lanzar ya, arreglar después.",
                      "B) Retrasar y arreglar ahora.",
                      "C) Lanzamiento limitado.",
                      "D) Escalar al Consejo."])
         else:
              return (f"Pregunta {num_pregunta}: Consecuencias del lanzamiento...", ["Opción X", "Opción Y", "Opción Z", "Opción W"])
    elif "Vertido Contaminante" in contexto:
        if num_pregunta == 1:
             return ("¿Cuál es tu primer paso estratégico?",
                     ["A) Detener vertido, investigar, asumir costes.",
                      "B) Consultar a Legal discretamente.",
                      "C) Confrontar al anterior Director.",
                      "D) Mejoras graduales y discretas."])
        else:
             return (f"Pregunta {num_pregunta}: Reacción interna/externa...", ["Opción X", "Opción Y", "Opción Z", "Opción W"])
    else:
        return (f"Pregunta genérica {num_pregunta}", ["Op1", "Op2", "Op3", "Op4"])


def mock_evaluar_decision(contexto, pregunta, opcion_elegida, estado_actual, nivel):
    """ Simula la evaluación de la decisión y genera análisis/consecuencias """
    # Lógica MUY simplificada
    analisis = f"Análisis simulado para la opción '{opcion_elegida.split(')')[0]}'. Esta decisión tiene implicaciones éticas y prácticas..."
    consecuencias_texto = "Consecuencias simuladas: La situación financiera podría verse afectada, la reputación está en juego y el clima laboral podría cambiar."
    nuevo_contexto = f"Nuevo contexto simulado después de elegir '{opcion_elegida.split(')')[0]}'. La situación ha evolucionado. {contexto[:100]}..." # Generar un contexto más realista

    # Impacto simulado (ejemplo)
    impacto = {"financiera": 0, "reputacion": 0, "laboral": 0}
    if opcion_elegida.startswith("A"):
        impacto = {"financiera": -1, "reputacion": -1, "laboral": 0}
    elif opcion_elegida.startswith("B"):
        impacto = {"financiera": 0, "reputacion": +1, "laboral": -1}
    elif opcion_elegida.startswith("C"):
        impacto = {"financiera": 0, "reputacion": 0, "laboral": -2}
    elif opcion_elegida.startswith("D"):
        impacto = {"financiera": +1, "reputacion": 0, "laboral": +1}

    return analisis, consecuencias_texto, nuevo_contexto, impacto

# --- Funciones Reales de Gemini (Plantillas) ---

def generar_escenario_gemini(nivel):
    """ Genera 5 escenarios únicos para el nivel dado usando Gemini """
    if not GEMINI_AVAILABLE: return mock_generar_escenario(nivel) # Fallback
    # --- LLAMADA REAL A GEMINI API ---
    # Crear un prompt detallado pidiendo 5 escenarios en formato JSON,
    # especificando nivel, necesidad de título, trasfondo, estado inicial (0,0,0).
    # prompt = f"Genera 5 escenarios únicos de crisis empresariales en español para un nivel de dificultad '{nivel}'. ... (instrucciones detalladas de formato JSON)"
    # response = model.generate_content(prompt)
    # Parsear la respuesta JSON y devolver la lista de escenarios.
    # Manejar errores si la respuesta no es válida.
    # return parsed_response
    st.warning("Usando datos MOCK para escenarios. Implementar llamada real a Gemini.")
    return mock_generar_escenario(nivel) # Placeholder

def generar_pregunta_y_opciones_gemini(contexto, historial, estado, nivel):
    """ Genera la siguiente pregunta y opciones usando Gemini """
    if not GEMINI_AVAILABLE: return mock_generar_pregunta_y_opciones(contexto, historial, estado, nivel) # Fallback
    # --- LLAMADA REAL A GEMINI API ---
    # Crear prompt detallado con contexto actual, historial de decisiones (resumido),
    # estado de la compañía, y nivel. Pedir una pregunta relevante y 4 opciones
    # de opción múltiple en un formato específico (ej. JSON: {"pregunta": "...", "opciones": ["A)...", "B)..."]}).
    # prompt = f"Dado el contexto: '{contexto}', historial: {historial}, estado: {estado}, nivel: {nivel}, genera la siguiente pregunta ética/de negocio relevante y 4 opciones de respuesta en español. Formato: ..."
    # response = model.generate_content(prompt)
    # Parsear respuesta y devolver tupla (pregunta, [opciones]).
    # return parsed_pregunta, parsed_opciones
    st.warning("Usando datos MOCK para preguntas/opciones. Implementar llamada real a Gemini.")
    return mock_generar_pregunta_y_opciones(contexto, historial, estado, nivel) # Placeholder

def evaluar_decision_gemini(contexto, pregunta, opcion_elegida, estado_actual, nivel):
    """ Evalúa la decisión, genera análisis/consecuencias y nuevo contexto """
    if not GEMINI_AVAILABLE: return mock_evaluar_decision(contexto, pregunta, opcion_elegida, estado_actual, nivel) # Fallback
    # --- LLAMADA REAL A GEMINI API ---
    # Crear prompt detallado con contexto, pregunta, opción elegida, estado actual, nivel.
    # Pedir:
    # 1. Análisis de la decisión (texto).
    # 2. Descripción de consecuencias (texto).
    # 3. Impacto numérico en financiera, reputación, laboral (ej. JSON: {"impacto": {"financiera": -1, "reputacion": 0, "laboral": -1}}).
    # 4. Nuevo texto de contexto describiendo la evolución de la situación.
    # prompt = f"Evalúa la decisión '{opcion_elegida}' para la pregunta '{pregunta}' en el contexto '{contexto}' (estado: {estado_actual}, nivel: {nivel}). Proporciona análisis, consecuencias textuales, impacto numérico (financiera, reputacion, laboral) y el nuevo contexto resultante. Formato: ..."
    # response = model.generate_content(prompt)
    # Parsear respuesta y devolver tupla (analisis, cons_texto, nuevo_contexto, impacto_dict).
    # return parsed_analisis, parsed_cons_texto, parsed_nuevo_contexto, parsed_impacto
    st.warning("Usando datos MOCK para evaluación. Implementar llamada real a Gemini.")
    return mock_evaluar_decision(contexto, pregunta, opcion_elegida, estado_actual, nivel) # Placeholder


# --- Lógica de la Aplicación Streamlit ---

# Inicialización del estado de sesión si no existe
def inicializar_estado():
    if 'pagina_actual' not in st.session_state:
        st.session_state.pagina_actual = 'inicio' # 'inicio', 'simulacion', 'resultado'
    if 'nivel_dificultad' not in st.session_state:
        st.session_state.nivel_dificultad = "Principiante"
    if 'escenarios_disponibles' not in st.session_state:
        st.session_state.escenarios_disponibles = []
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

# --- Lógica de Páginas ---

# Página de Inicio
if st.session_state.pagina_actual == 'inicio':
    st.title("🚀 Simulador de Crisis Empresariales")
    st.markdown("Bienvenido/a. Selecciona un nivel y un escenario para comenzar a tomar decisiones críticas.")

    nivel = st.selectbox("Selecciona el Nivel de Dificultad:",
                         ["Principiante", "Intermedio", "Avanzado"],
                         index=["Principiante", "Intermedio", "Avanzado"].index(st.session_state.nivel_dificultad))

    # Si cambia el nivel, recargar escenarios
    if nivel != st.session_state.nivel_dificultad:
        st.session_state.nivel_dificultad = nivel
        st.session_state.escenarios_disponibles = generar_escenario_gemini(nivel) # O mock_generar_escenario(nivel)
        st.session_state.escenario_seleccionado_id = None # Resetear selección
        st.rerun() # Volver a ejecutar para actualizar el selectbox de escenarios

    # Cargar escenarios si están vacíos para el nivel actual
    if not st.session_state.escenarios_disponibles:
         st.session_state.escenarios_disponibles = generar_escenario_gemini(st.session_state.nivel_dificultad)

    if st.session_state.escenarios_disponibles:
        opciones_escenario = {esc['id']: esc['titulo'] for esc in st.session_state.escenarios_disponibles}
        escenario_id = st.selectbox("Selecciona un Escenario:",
                                    options=list(opciones_escenario.keys()),
                                    format_func=lambda x: opciones_escenario[x])

        if st.button("Iniciar Simulación"):
            st.session_state.escenario_seleccionado_id = escenario_id
            # Encontrar los datos completos del escenario seleccionado
            st.session_state.datos_escenario = next((esc for esc in st.session_state.escenarios_disponibles if esc['id'] == escenario_id), None)

            if st.session_state.datos_escenario:
                # Resetear estado para nueva simulación
                st.session_state.estado_simulacion = st.session_state.datos_escenario['estado_inicial'].copy()
                st.session_state.estado_anterior = st.session_state.estado_simulacion.copy()
                st.session_state.numero_pregunta = 0
                st.session_state.contexto_actual = st.session_state.datos_escenario['trasfondo']
                st.session_state.historial_decisiones = []
                st.session_state.ultimo_analisis = ""
                st.session_state.ultimas_consecuencias = ""
                st.session_state.juego_terminado = False
                st.session_state.razon_fin = ""
                st.session_state.puntaje_final = 0

                # Generar la primera pregunta
                pregunta, opciones = generar_pregunta_y_opciones_gemini(
                    st.session_state.contexto_actual,
                    st.session_state.historial_decisiones,
                    st.session_state.estado_simulacion,
                    st.session_state.nivel_dificultad
                )
                st.session_state.pregunta_actual = pregunta
                st.session_state.opciones_actuales = opciones
                st.session_state.numero_pregunta = 1 # Empezamos con la pregunta 1

                # Cambiar a la página de simulación
                st.session_state.pagina_actual = 'simulacion'
                st.rerun() # Volver a ejecutar para mostrar la página de simulación
            else:
                st.error("Error al cargar los datos del escenario.")
    else:
        st.warning(f"No hay escenarios disponibles para el nivel {st.session_state.nivel_dificultad}. Verifica la función de generación.")


# Página de Simulación
elif st.session_state.pagina_actual == 'simulacion':
    if not st.session_state.datos_escenario:
        st.error("Error: No se ha cargado ningún escenario. Volviendo al inicio.")
        st.session_state.pagina_actual = 'inicio'
        time.sleep(2) # Pequeña pausa antes de redirigir
        st.rerun()
    else:
        st.title(f"Simulación: {st.session_state.datos_escenario['titulo']}")

        # Mostrar estado actual con deltas
        col1, col2, col3 = st.columns(3)
        delta_fin = st.session_state.estado_simulacion['financiera'] - st.session_state.estado_anterior['financiera']
        delta_rep = st.session_state.estado_simulacion['reputacion'] - st.session_state.estado_anterior['reputacion']
        delta_lab = st.session_state.estado_simulacion['laboral'] - st.session_state.estado_anterior['laboral']

        col1.metric("💰 Situación Financiera", st.session_state.estado_simulacion['financiera'], delta=f"{delta_fin:+}" if delta_fin else None)
        col2.metric("📈 Reputación", st.session_state.estado_simulacion['reputacion'], delta=f"{delta_rep:+}" if delta_rep else None)
        col3.metric("👥 Clima Laboral", st.session_state.estado_simulacion['laboral'], delta=f"{delta_lab:+}" if delta_lab else None)

        # Barra de progreso
        st.progress(st.session_state.numero_pregunta / 10)
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
        st.markdown(st.session_state.pregunta_actual)

        user_choice = st.radio("Selecciona tu decisión:",
                               st.session_state.opciones_actuales,
                               index=None, # Para que no haya selección por defecto
                               key=f"q_{st.session_state.numero_pregunta}") # Key única por pregunta

        if st.button("Confirmar Decisión", key=f"b_{st.session_state.numero_pregunta}"):
            if user_choice:
                # Guardar estado anterior para calcular deltas en la próxima iteración
                st.session_state.estado_anterior = st.session_state.estado_simulacion.copy()

                # Procesar decisión
                st.session_state.historial_decisiones.append({"pregunta": st.session_state.pregunta_actual, "respuesta": user_choice})

                # Evaluar decisión (usando mock o real)
                analisis, cons_texto, nuevo_contexto, impacto = evaluar_decision_gemini(
                    st.session_state.contexto_actual,
                    st.session_state.pregunta_actual,
                    user_choice,
                    st.session_state.estado_simulacion,
                    st.session_state.nivel_dificultad
                )

                # Actualizar estado de la simulación
                st.session_state.estado_simulacion['financiera'] += impacto.get('financiera', 0)
                st.session_state.estado_simulacion['reputacion'] += impacto.get('reputacion', 0)
                st.session_state.estado_simulacion['laboral'] += impacto.get('laboral', 0)

                st.session_state.contexto_actual = nuevo_contexto
                st.session_state.ultimo_analisis = analisis
                st.session_state.ultimas_consecuencias = cons_texto

                # Verificar condiciones de fin
                if st.session_state.numero_pregunta >= 10:
                    st.session_state.juego_terminado = True
                    st.session_state.razon_fin = "Se completaron las 10 preguntas."
                elif st.session_state.estado_simulacion['financiera'] <= -10: # Umbral de bancarrota (ejemplo)
                    st.session_state.juego_terminado = True
                    st.session_state.razon_fin = "¡Bancarrota! La situación financiera colapsó."
                # Podría haber otras condiciones de fin (ej. reputación muy baja)

                if st.session_state.juego_terminado:
                    # Calcular puntaje final
                    st.session_state.puntaje_final = (
                        st.session_state.estado_simulacion['financiera'] +
                        st.session_state.estado_simulacion['reputacion'] +
                        st.session_state.estado_simulacion['laboral']
                    )
                    st.session_state.pagina_actual = 'resultado'
                else:
                    # Pasar a la siguiente pregunta
                    st.session_state.numero_pregunta += 1
                    pregunta, opciones = generar_pregunta_y_opciones_gemini(
                        st.session_state.contexto_actual,
                        st.session_state.historial_decisiones,
                        st.session_state.estado_simulacion,
                        st.session_state.nivel_dificultad
                    )
                    st.session_state.pregunta_actual = pregunta
                    st.session_state.opciones_actuales = opciones

                st.rerun() # Actualizar la interfaz

            else:
                st.warning("Por favor, selecciona una opción antes de confirmar.")

# Página de Resultados
elif st.session_state.pagina_actual == 'resultado':
    st.title("🏁 Resultados de la Simulación")
    st.subheader(f"Escenario: {st.session_state.datos_escenario.get('titulo', 'Desconocido')}")

    st.markdown(f"**Razón del Fin:** {st.session_state.razon_fin}")
    st.markdown("---")
    st.subheader("Estado Final de la Compañía:")

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Situación Financiera Final", st.session_state.estado_simulacion['financiera'])
    col2.metric("📈 Reputación Final", st.session_state.estado_simulacion['reputacion'])
    col3.metric("👥 Clima Laboral Final", st.session_state.estado_simulacion['laboral'])

    st.markdown("---")
    st.subheader("Puntaje Total:")
    # Puedes añadir una interpretación del puntaje aquí
    st.metric("🏆 Puntaje Final", st.session_state.puntaje_final)
    if st.session_state.puntaje_final > 5:
        st.success("¡Excelente gestión de la crisis!")
    elif st.session_state.puntaje_final < -5:
        st.error("La gestión de la crisis tuvo resultados muy negativos.")
    else:
        st.info("La gestión de la crisis tuvo un resultado mixto.")

    st.markdown("---")
    if st.button("Volver al Inicio"):
        # Resetear estado para permitir nueva partida
        st.session_state.pagina_actual = 'inicio'
        # Opcional: podrías resetear más estados si es necesario, pero
        # la lógica de 'Iniciar Simulación' ya resetea lo principal.
        st.session_state.escenario_seleccionado_id = None
        st.session_state.datos_escenario = None
        st.rerun()
