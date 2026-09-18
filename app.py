"""VALOR — Point d'entrée : config globale + navigation horizontale."""
import streamlit as st
from utils.theme import inject_css

st.set_page_config(
    page_title="VALOR — Big 5",
    page_icon="⚽",
    layout="wide",
)
inject_css()

pages = [
    st.Page("views/page_accueil.py", title="Accueil", icon="⚽", default=True),
    st.Page("views/page_classement.py", title="Classement", icon="📊"),
    st.Page("views/page_profil_joueur.py", title="Profil joueur", icon="🎯"),
    st.Page("views/page_comparateur.py", title="Comparateur", icon="⚔️"),
    st.Page("views/page_scatter_valor.py", title="Scatter VALOR", icon="📈"),
]

st.navigation(pages, position="top").run()
