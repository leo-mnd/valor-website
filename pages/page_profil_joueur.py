"""Profil joueur avec radar."""
import streamlit as st
import pandas as pd
from utils.data_loader import load_valor_data, get_position_label
from utils.charts import player_radar


st.set_page_config(page_title="Profil joueur — VALOR", page_icon="🎯", layout="wide")

df = load_valor_data()

st.title("🎯 Profil joueur")

# --- Selection joueur ---
joueurs = sorted(df["Player"].unique())
joueur_select = st.selectbox(
    "Choisis un joueur",
    options=joueurs,
    index=joueurs.index("Ousmane Dembélé") if "Ousmane Dembélé" in joueurs else 0,
)

player = df[df["Player"] == joueur_select].iloc[0]

# --- Fiche joueur ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("VALOR", f"{player['VALOR']:.1f}")
col2.metric("Rang general", f"#{int(player['Rang'])}")
col3.metric("Poste", get_position_label(player["valor_position_12"]))
col4.metric("Equipe", player["Squad"])

st.markdown("---")

# --- Stats brutes ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Stats saison")
    st.markdown(f"**Age** : {int(player['Age']) if not pd.isna(player.get('Age', None)) else 'N/A'}")
    st.markdown(f"**Nation** : {player.get('Nation', 'N/A')}")
    st.markdown(f"**Minutes (club principal)** : {int(player['PlayingTime_Min'])}")
    st.markdown(f"**Buts** : {int(player.get('Performance_Gls', 0))}")
    st.markdown(f"**Passes decisives** : {int(player.get('Performance_Ast', 0))}")
    st.markdown(f"**xG** : {player.get('us_xG_season', 0):.2f}")
    st.markdown(f"**xA** : {player.get('us_xA_season', 0):.2f}")
    st.markdown(f"**Tacles gagnes** : {int(player.get('fbref_tackles_won', 0))}")
    st.markdown(f"**Interceptions** : {int(player.get('fbref_interceptions', 0))}")

with col2:
    st.subheader("Profil radar (z-scores positionnels)")
    
    # Selection des metriques selon le poste
    poste = player["valor_position_calc"]
    
    metrics_by_position = {
        "CB": ["int_p90_adj_z", "tkl_won_p90_adj_z", "us_xgbuildup_p90_adj_z", "us_xgchain_p90_adj_z"],
        "FB_L": ["int_p90_adj_z", "tkl_won_p90_adj_z", "crs_p90_adj_z",
                 "us_xgbuildup_p90_adj_z", "us_xgchain_p90_adj_z",
                 "us_kp_p90_adj_z", "us_xa_p90_adj_z"],
        "FB_R": ["int_p90_adj_z", "tkl_won_p90_adj_z", "crs_p90_adj_z",
                 "us_xgbuildup_p90_adj_z", "us_xgchain_p90_adj_z",
                 "us_kp_p90_adj_z", "us_xa_p90_adj_z"],
        "DM": ["int_p90_adj_z", "tkl_won_p90_adj_z",
               "us_xgbuildup_p90_adj_z", "us_xgchain_p90_adj_z",
               "us_kp_p90_adj_z", "us_xa_p90_adj_z"],
        "CM": ["int_p90_adj_z", "tkl_won_p90_adj_z",
               "us_xgchain_p90_adj_z", "us_xgbuildup_p90_adj_z",
               "us_kp_p90_adj_z", "us_xa_p90_adj_z", "ast_p90_adj_z",
               "gls_p90_adj_z", "us_xg_p90_adj_z"],
        "AM": ["int_p90_adj_z", "tkl_won_p90_adj_z",
               "us_xgbuildup_p90_adj_z", "us_xgchain_p90_adj_z",
               "us_kp_p90_adj_z", "us_xa_p90_adj_z", "ast_p90_adj_z",
               "us_shots_p90_adj_z", "gls_p90_adj_z", "us_xg_p90_adj_z"],
        "W_L": ["us_xgbuildup_p90_adj_z", "us_xgchain_p90_adj_z",
                "us_kp_p90_adj_z", "us_xa_p90_adj_z",
                "us_shots_p90_adj_z", "us_xg_p90_adj_z",
                "gls_p90_adj_z", "crs_p90_adj_z",
                "fls_drawn_p90_adj_z", "ast_p90_adj_z"],
        "W_R": ["us_xgbuildup_p90_adj_z", "us_xgchain_p90_adj_z",
                "us_kp_p90_adj_z", "us_xa_p90_adj_z",
                "us_shots_p90_adj_z", "us_xg_p90_adj_z",
                "gls_p90_adj_z", "crs_p90_adj_z",
                "fls_drawn_p90_adj_z", "ast_p90_adj_z"],
        "ST": ["us_xgbuildup_p90_adj_z", "us_xgchain_p90_adj_z",
               "us_kp_p90_adj_z", "us_xa_p90_adj_z",
               "us_shots_p90_adj_z", "us_xg_p90_adj_z",
               "gls_p90_adj_z", "ast_p90_adj_z",
               "fls_drawn_p90_adj_z"],
    }
    
    metrics = metrics_by_position.get(poste, metrics_by_position["CM"])
    fig = player_radar(player, metrics, title=f"{player['Player']} ({get_position_label(player['valor_position_12'])})")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- Methodologie / explication ---
with st.expander("Comment lire ce radar ?"):
    st.markdown("""
    Le radar affiche les **z-scores positionnels** du joueur, transformes en echelle 0-100 :
    - **50** = la moyenne du poste
    - **80** = top 10% du poste
    - **95** = top 5% du poste
    
    Les metriques affichees correspondent a celles utilisees dans le calcul VALOR pour ce poste.
    Les poids tactiques par poste sont disponibles dans la documentation methodologique.
    """)