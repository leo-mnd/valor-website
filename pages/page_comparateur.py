"""Comparateur de 2 joueurs."""
import streamlit as st
import pandas as pd
from utils.data_loader import load_valor_data, get_position_label
from utils.charts import comparison_radar


st.set_page_config(page_title="Comparateur — VALOR", page_icon="⚔️", layout="wide")

df = load_valor_data()

st.title("⚔️ Comparateur de joueurs")
st.markdown("Compare 2 joueurs sur leur profil tactique respectif.")

# --- Selection 2 joueurs ---
joueurs = sorted(df["Player"].unique())

col1, col2 = st.columns(2)

with col1:
    j1 = st.selectbox(
        "Joueur 1",
        options=joueurs,
        index=joueurs.index("Ousmane Dembélé") if "Ousmane Dembélé" in joueurs else 0,
        key="j1",
    )

with col2:
    j2 = st.selectbox(
        "Joueur 2",
        options=joueurs,
        index=joueurs.index("Mason Greenwood") if "Mason Greenwood" in joueurs else 1,
        key="j2",
    )

if j1 == j2:
    st.warning("Choisis 2 joueurs differents !")
    st.stop()

player1 = df[df["Player"] == j1].iloc[0]
player2 = df[df["Player"] == j2].iloc[0]

# --- Headers comparatifs ---
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"🔵 {player1['Player']}")
    st.markdown(f"**{player1['Squad']}** • {get_position_label(player1['valor_position_12'])}")
    col1a, col1b = st.columns(2)
    col1a.metric("VALOR", f"{player1['VALOR']:.1f}")
    col1b.metric("Rang", f"#{int(player1['Rang'])}")

with col2:
    st.subheader(f"🔴 {player2['Player']}")
    st.markdown(f"**{player2['Squad']}** • {get_position_label(player2['valor_position_12'])}")
    col2a, col2b = st.columns(2)
    col2a.metric("VALOR", f"{player2['VALOR']:.1f}")
    col2b.metric("Rang", f"#{int(player2['Rang'])}")

# --- Radar comparatif ---
st.markdown("---")
st.subheader("Comparaison radar")

# Pour les radars comparatifs : on prend l'intersection des metriques des 2 postes
# ou un set commun de metriques offensives core
common_metrics = [
    "gls_p90_adj_z", "ast_p90_adj_z",
    "us_xg_p90_adj_z", "us_xa_p90_adj_z",
    "us_shots_p90_adj_z", "us_kp_p90_adj_z",
    "us_xgchain_p90_adj_z", "us_xgbuildup_p90_adj_z",
    "tkl_won_p90_adj_z", "int_p90_adj_z",
    "crs_p90_adj_z", "fls_drawn_p90_adj_z",
]

if player1["valor_position_12"] != player2["valor_position_12"]:
    st.info(
        f"⚠️ Les 2 joueurs jouent a des postes differents "
        f"({get_position_label(player1['valor_position_12'])} vs "
        f"{get_position_label(player2['valor_position_12'])}). "
        f"Le radar utilise des metriques generales, mais les z-scores sont calcules "
        f"par rapport au poste de chaque joueur."
    )

fig = comparison_radar(player1, player2, common_metrics)
st.plotly_chart(fig, use_container_width=True)

# --- Tableau comparatif ---
st.markdown("---")
st.subheader("Stats saison")

stats_compare = pd.DataFrame({
    "Stat": ["Minutes", "Buts", "Passes decisives", "xG", "xA",
             "Tacles gagnes", "Interceptions"],
    player1["Player"]: [
        int(player1["PlayingTime_Min"]),
        int(player1.get("Performance_Gls", 0)),
        int(player1.get("Performance_Ast", 0)),
        f"{player1.get('us_xG_season', 0):.2f}",
        f"{player1.get('us_xA_season', 0):.2f}",
        int(player1.get("fbref_tackles_won", 0)),
        int(player1.get("fbref_interceptions", 0)),
    ],
    player2["Player"]: [
        int(player2["PlayingTime_Min"]),
        int(player2.get("Performance_Gls", 0)),
        int(player2.get("Performance_Ast", 0)),
        f"{player2.get('us_xG_season', 0):.2f}",
        f"{player2.get('us_xA_season', 0):.2f}",
        int(player2.get("fbref_tackles_won", 0)),
        int(player2.get("fbref_interceptions", 0)),
    ],
})

st.dataframe(stats_compare, hide_index=True, use_container_width=True)