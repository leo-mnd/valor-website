"""Scatter plot VALOR vs Minutes par poste."""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import (
    load_valor_data, get_position_label,
    league_selector, season_selector, LEAGUES, SEASONS
)
from utils.theme import inject_css

st.set_page_config(page_title="Scatter VALOR — VALOR", page_icon="📈", layout="wide")
inject_css()

# --- Sélecteurs (sidebar) ---
league_slug = league_selector(default="ligue1", key="scatter_league")
league_display = LEAGUES[league_slug]["display"]
season_slug = season_selector(default="2025_2026", key="scatter_season")
season_display = SEASONS[season_slug]["display"]

# --- Charger la data ---
df = load_valor_data(league_slug, season_slug)

# --- Sélecteur poste ---
st.sidebar.markdown("---")
positions_dispo = sorted(df["valor_position_12"].unique())
poste_default_idx = positions_dispo.index("ST") if "ST" in positions_dispo else 0
poste_select = st.sidebar.selectbox(
    "🎯 Poste",
    options=positions_dispo,
    index=poste_default_idx,
    format_func=lambda x: f"{x} ({get_position_label(x)})",
    key="scatter_poste",
)

# --- Filtrer et préparer ---
df_filtered = df[df["valor_position_12"] == poste_select].copy()

# --- Header ---
st.title("📈 Scatter VALOR")
st.markdown(f"**{league_display} — {season_display}** | Poste : {get_position_label(poste_select)} ({len(df_filtered)} joueurs)")
st.markdown("---")

# --- Guardrail si peu de joueurs ---
if len(df_filtered) == 0:
    st.warning(f"Aucun joueur pour le poste {poste_select} dans cette ligue/saison.")
    st.stop()

# --- Scatter plot Plotly ---
fig = px.scatter(
    df_filtered,
    x="VALOR",
    y="total_minutes_season",
    hover_data={
        "Player": True,
        "Squad": True,
        "VALOR": ":.1f",
        "total_minutes_season": True,
        "valor_position_12": False,
    },
    color="VALOR",
    color_continuous_scale="Viridis",
    labels={
        "VALOR": "VALOR",
        "total_minutes_season": "Minutes jouées",
    },
    title=f"Distribution VALOR × Minutes — {get_position_label(poste_select)} — {league_display} {season_display}",
    height=650,
    template="plotly_dark",
)

fig.update_traces(
    marker=dict(size=12, line=dict(width=1, color="rgba(255,255,255,0.3)")),
)

fig.update_layout(
    xaxis_title="VALOR",
    yaxis_title="Minutes jouées sur la saison",
    plot_bgcolor="#0e1117",
    paper_bgcolor="#0e1117",
    font=dict(color="white", size=13),
    hoverlabel=dict(bgcolor="#262730", font_size=13, font_color="white"),
    title_font=dict(size=16),
    xaxis=dict(gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.2)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.2)"),
)

# Lignes de repères sans annotation (pour éviter chevauchement avec la barre couleur)
fig.add_hline(y=1200, line_dash="dash", line_color="rgba(255,255,255,0.4)", opacity=0.7)
fig.add_vline(x=50, line_dash="dot", line_color="rgba(255,255,255,0.3)", opacity=0.5)

st.plotly_chart(fig, use_container_width=True)

# --- Légende sous le graph ---
st.markdown("""
<div style="font-size:12px; color:#888; margin-top:-15px;">
📏 <b>Ligne horizontale (pointillés) :</b> seuil 1200 min (bonus/malus SSS)
&nbsp;&nbsp;·&nbsp;&nbsp;
📊 <b>Ligne verticale (pointillés) :</b> VALOR = 50 (moyenne théorique)
</div>
""", unsafe_allow_html=True)

# --- Légende / interprétation ---
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

# Top VALOR
top_valor = df_filtered.nlargest(5, "VALOR")[["Player", "Squad", "VALOR", "total_minutes_season"]]
col1.markdown("**🏆 Top 5 VALOR**")
for _, r in top_valor.iterrows():
    col1.markdown(f"  {r['Player']} ({r['VALOR']:.1f}, {r['total_minutes_season']}′)")

# Joueurs élites qui jouent le plus
mask_elite = (df_filtered["VALOR"] > df_filtered["VALOR"].median()) & (df_filtered["total_minutes_season"] > 2000)
col2.markdown("**⭐ Élites avec >2000′**")
elites = df_filtered[mask_elite].nlargest(5, "VALOR")[["Player", "Squad", "VALOR"]]
for _, r in elites.iterrows():
    col2.markdown(f"  {r['Player']} ({r['VALOR']:.1f})")

# Diamants bruts (VALOR élevé, peu de minutes)
mask_gems = (df_filtered["VALOR"] > 65) & (df_filtered["total_minutes_season"] < 1200)
gems = df_filtered[mask_gems].nlargest(5, "VALOR")[["Player", "Squad", "VALOR", "total_minutes_season"]]
col3.markdown("**💎 Diamants bruts (<1200′)**")
for _, r in gems.iterrows():
    col3.markdown(f"  {r['Player']} ({r['VALOR']:.1f}, {r['total_minutes_season']}′)")

# Utilisation vs Impact
col4.markdown("**📊 Stats globales**")
col4.markdown(f"VALOR moyen : {df_filtered['VALOR'].mean():.1f}")
col4.markdown(f"VALOR médian : {df_filtered['VALOR'].median():.1f}")
col4.markdown(f"Min moyennes : {df_filtered['total_minutes_season'].mean():.0f}")
col4.markdown(f"Nb de joueurs : {len(df_filtered)}")