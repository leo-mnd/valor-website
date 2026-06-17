"""VALOR — Page d'accueil."""
import streamlit as st
from utils.data_loader import load_valor_data, get_position_label


st.set_page_config(
    page_title="VALOR — Ligue 1 2024-25",
    page_icon="⚽",
    layout="wide",
)

df = load_valor_data()

# --- Header ---
st.title("⚽ VALOR")
st.subheader("Valuation Analytics for League Optimized Rating")
st.markdown("**Ligue 1 2024-2025 — MVP**")

st.markdown("---")

# --- KPIs ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Joueurs notes", f"{len(df)}")
col2.metric("Equipes couvertes", f"{df['Squad'].nunique()}")
col3.metric("Postes", "11 (hors GK)")
col4.metric("VALOR max", f"{df['VALOR'].max():.1f}")

st.markdown("---")

# --- Top 10 ---
st.subheader("Top 10 general")
top10 = df.head(10)[["Rang", "Player", "Squad", "valor_position_12", "PlayingTime_Min", "VALOR"]]
top10 = top10.rename(columns={
    "valor_position_12": "Poste",
    "PlayingTime_Min": "Minutes",
})
st.dataframe(top10, hide_index=True, use_container_width=True)

st.markdown("---")

# --- Pitch méthodologique ---
st.subheader("Qu'est-ce que VALOR ?")
st.markdown("""
VALOR est un systeme de notation des joueurs de football conçu pour combiner **rigueur analytique**
et **transparence methodologique**.

**Ce qui distingue VALOR :**

- **Transparence** : toutes les pondérations et choix sont publics
- **Grille tactique par poste** : 11 grilles distinctes (CB, FB, DM, CM, AM, W, ST...)
- **Ajustement contextuel** : un attaquant d'equipe faible n'est pas penalise pour son systeme
- **Open source** : la methodologie complete est documentee

Navigue dans les pages a gauche pour explorer le classement complet, les profils par joueur,
ou comparer deux joueurs entre eux.
""")

# --- Footer ---
st.markdown("---")
st.caption("VALOR MVP — Solo project par Jules — juin 2026")