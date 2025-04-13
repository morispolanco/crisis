import streamlit as st

st.set_page_config(layout="wide", page_title="Contacto - Simulador de Crisis")

st.title("Contacto")

st.markdown("""
Para consultas, sugerencias o información adicional sobre esta aplicación, por favor contactar a:

**Moris Polanco**

*   **Email:** [mp@ufm.edu](mailto:mp@ufm.edu)
*   **Página Web:** [morispolanco.vercel.app](https://morispolanco.vercel.app)

""")

st.markdown("---")
st.info("📧 No dudes en enviar tus comentarios para ayudar a mejorar esta herramienta.")

# Añadir barra lateral consistente si se desea (opcional)
# st.sidebar.title("Navegación")
# st.sidebar.page_link("app.py", label="Inicio / Simulación")
# st.sidebar.page_link("pages/acerca_de.py", label="Acerca de")
# st.sidebar.page_link("pages/contacto.py", label="Contacto")
