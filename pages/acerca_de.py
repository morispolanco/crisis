import streamlit as st

st.set_page_config(layout="wide", page_title="Acerca de - Simulador de Crisis")

st.title("Acerca de la Aplicación")

st.markdown("""
Esta aplicación es un **Simulador Avanzado de Crisis Empresariales** diseñado como herramienta educativa interactiva.

**Propósito:**
Ayudar a los usuarios a desarrollar habilidades de toma de decisiones éticas y estratégicas en situaciones complejas del mundo empresarial. La aplicación presenta escenarios realistas donde las decisiones tienen consecuencias medibles en la salud financiera, la reputación y el ambiente laboral de una empresa ficticia.

**Cómo Funciona:**
1.  **Selección:** Elige un nivel de dificultad (Principiante, Intermedio, Avanzado) y uno de los cinco escenarios disponibles para ese nivel.
2.  **Simulación:** Se presenta un contexto inicial y el estado de la empresa (Finanzas, Reputación, Clima Laboral). Deberás responder a 10 preguntas de opción múltiple que representan decisiones críticas.
3.  **Evolución:** Cada decisión es analizada y tiene consecuencias que modifican el estado de la empresa y el contexto de la crisis. La situación evoluciona dinámicamente.
4.  **Resultado:** La simulación termina después de 10 preguntas o si la empresa alcanza un estado crítico (ej. bancarrota). Recibirás un puntaje final basado en el estado de la empresa.

**Tecnología:**
*   **Interfaz:** Desarrollada con [Streamlit](https://streamlit.io/), un marco de trabajo Python para crear aplicaciones web de datos de forma rápida.
*   **Inteligencia Artificial:** Utiliza la **API de Google Gemini** para generar dinámicamente los escenarios, las preguntas contextuales, los análisis de decisiones y las consecuencias, proporcionando una experiencia rica y variada.
*   **Lenguaje:** Todo el contenido y la lógica están implementados en Python.

**Valor Educativo:**
Este simulador fomenta el pensamiento crítico, la evaluación de riesgos, la consideración de múltiples partes interesadas (multi-agente) y la comprensión de las implicaciones éticas en la gestión empresarial.

---
*Desarrollado como un proyecto avanzado de simulación.*
""")

# Añadir barra lateral consistente si se desea (opcional, ya que Streamlit la maneja por defecto)
# st.sidebar.title("Navegación")
# st.sidebar.page_link("app.py", label="Inicio / Simulación")
# st.sidebar.page_link("pages/acerca_de.py", label="Acerca de")
# st.sidebar.page_link("pages/contacto.py", label="Contacto")
