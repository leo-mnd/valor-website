"""VALOR — Page d'accueil."""
import streamlit as st
from utils.data_loader import (
    load_valor_data, get_position_label,
    league_selector, season_selector, LEAGUES, SEASONS
)

st.set_page_config(
    page_title="VALOR — Big 5",
    page_icon="⚽",
    layout="wide",
)

# --- Sélecteurs (sidebar) ---
league_slug = league_selector(default="ligue1")
league_display = LEAGUES[league_slug]["display"]
season_slug = season_selector(default="2025_2026")
season_display = SEASONS[season_slug]["display"]

# --- Charger la data ---
df = load_valor_data(league_slug, season_slug)

# --- Header ---
st.title("⚽ VALOR")
st.subheader("Valuation Analytics for League Optimized Rating")
st.markdown(f"**{league_display} — {season_display}**")
st.markdown("---")

# --- KPIs ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Joueurs notés", f"{len(df)}")
col2.metric("Équipes couvertes", f"{df['Squad'].nunique()}")
col3.metric("Postes", "11 (hors GK)")
col4.metric("VALOR max", f"{df['VALOR'].max():.1f}")

st.markdown("---")

# --- Top 10 ---
st.markdown(f"### 🏆 Top 10 — {league_display} {season_display}")
top10 = df.nlargest(10, "VALOR")[["Rang", "Player", "Squad", "valor_position_12", "VALOR"]].copy()
top10["Poste"] = top10["valor_position_12"].apply(get_position_label)
top10 = top10[["Rang", "Player", "Squad", "Poste", "VALOR"]]
top10.columns = ["Rang", "Joueur", "Équipe", "Poste", "VALOR"]
st.dataframe(top10, hide_index=True, width="stretch")

# --- Info ---
st.markdown("---")
st.markdown("""
💡 **Comment lire VALOR ?**
Le score VALOR (0-100) évalue chaque joueur selon sa position tactique, ses statistiques par 90 minutes,
et le contexte de son équipe (SoS = Strength of Schedule). Un ajustement volume récompense les joueurs avec une saison complète (+5 max)
et pénalise les petits échantillons (-8 max) pour éviter les biais.

📊 Utilise le menu latéral pour explorer le **classement complet**, un **profil joueur**, ou **comparer** deux joueurs.
""")