"""Profil joueur — avec évolution intersaisons, radar et similar players."""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.data_loader import (
    load_valor_data, load_all_leagues_season,
    get_position_label, get_metric_label,
    league_selector, season_selector, LEAGUES, SEASONS
)
from utils.charts import player_radar


# --- Sélecteurs ---
league_slug = league_selector(default="ligue1", key="profil_league")
league_display = LEAGUES[league_slug]["display"]
season_slug = season_selector(default="2025_2026", key="profil_season")
season_display = SEASONS[season_slug]["display"]

df = load_valor_data(league_slug, season_slug)

st.title("🎯 Profil joueur")

# --- Sélection joueur ---
joueurs = sorted(df["Player"].unique())
default_idx = joueurs.index("Ousmane Dembélé") if "Ousmane Dembélé" in joueurs else 0
player_name = st.selectbox("Joueur", options=joueurs, index=default_idx, key="profil_player")

player = df[df["Player"] == player_name].iloc[0]
poste = player["valor_position_12"]

# --- HEADER ---
st.markdown("---")
col_h1, col_h2, col_h3, col_h4 = st.columns(4)
col_h1.metric("Club", player["Squad"])
col_h2.metric("Poste", get_position_label(poste))
col_h3.metric("VALOR", f"{player['VALOR']:.1f}")
col_h4.metric("Rang ligue", f"#{int(player['Rang'])}")

st.markdown("---")

# --- Charger la saison précédente pour évolution ---
prev_season_slug = "2024_2025" if season_slug == "2025_2026" else None
player_prev = None
if prev_season_slug:
    try:
        df_prev = load_valor_data(league_slug, prev_season_slug)
        matches = df_prev[df_prev["Player"] == player_name]
        if len(matches) > 0:
            player_prev = matches.iloc[0]
    except Exception:
        pass

# --- Métriques par poste pour tableau ---
STATS_BY_POSITION = {
    "GK": ["Buts encaissés", "Clean sheets"],  # à améliorer si on a les stats GK
    "CB": [
        ("Interceptions/90", "int_p90"),
        ("Tacles gagnés/90", "tkl_won_p90"),
        ("xGBuildup", "us_xgbuildup_season"),
        ("xGChain", "us_xgchain_season"),
    ],
    "FB_L": [
        ("Centres/90", "crs_p90"),
        ("PD/90", "ast_p90"),
        ("Tacles/90", "tkl_won_p90"),
        ("xA saison", "us_xA_season"),
    ],
    "FB_R": [
        ("Centres/90", "crs_p90"),
        ("PD/90", "ast_p90"),
        ("Tacles/90", "tkl_won_p90"),
        ("xA saison", "us_xA_season"),
    ],
    "DM": [
        ("Interceptions/90", "int_p90"),
        ("Tacles/90", "tkl_won_p90"),
        ("Fautes commises/90", "fls_committed_p90"),
        ("xGBuildup", "us_xgbuildup_season"),
    ],
    "CM": [
        ("PD/90", "ast_p90"),
        ("xA/90", "us_xa_p90"),
        ("Passes clés/90", "us_kp_p90"),
        ("Interceptions/90", "int_p90"),
    ],
    "AM": [
        ("Passes clés/90", "us_kp_p90"),
        ("xA/90", "us_xa_p90"),
        ("PD/90", "ast_p90"),
        ("xG/90", "us_xg_p90"),
    ],
    "W_L": [
        ("Buts/90", "us_gls_p90"),
        ("xG/90", "us_xg_p90"),
        ("Passes clés/90", "us_kp_p90"),
        ("Fautes drawn/90", "fls_drawn_p90"),
    ],
    "W_R": [
        ("Buts/90", "us_gls_p90"),
        ("xG/90", "us_xg_p90"),
        ("Passes clés/90", "us_kp_p90"),
        ("Fautes drawn/90", "fls_drawn_p90"),
    ],
    "ST": [
        ("Buts/90", "us_gls_p90"),
        ("xG/90", "us_xg_p90"),
        ("Tirs/90", "us_shots_p90"),
        ("Fautes drawn/90", "fls_drawn_p90"),
    ],
}

# Fallback si poste non prévu
stats_config = STATS_BY_POSITION.get(poste, [
    ("Buts saison", "us_goals_season"),
    ("Assists saison", "us_assists_season"),
    ("xG saison", "us_xG_season"),
])

# --- LIGNE 1 : Haut gauche (tableau) + Haut droite (radar) ---
col_top_left, col_top_right = st.columns([1, 1])

with col_top_left:
    st.subheader(f"📊 Évolution intersaisons")
    
    # Construction du tableau
    rows = [("VALOR", f"{player['VALOR']:.1f}",
             f"{player_prev['VALOR']:.1f}" if player_prev is not None else "N/A",
             f"{player['VALOR'] - player_prev['VALOR']:+.1f}" if player_prev is not None else "-")]
    rows.append(("Rang ligue", f"#{int(player['Rang'])}",
                 f"#{int(player_prev['Rang'])}" if player_prev is not None else "N/A",
                 f"{int(player_prev['Rang']) - int(player['Rang']):+d} positions" if player_prev is not None else "-"))
    rows.append(("Minutes", str(int(player["total_minutes_season"])),
                 str(int(player_prev["total_minutes_season"])) if player_prev is not None else "N/A",
                 f"{int(player['total_minutes_season']) - int(player_prev['total_minutes_season']):+d}" if player_prev is not None else "-"))
    
    # Ajout des stats poste-spécifiques
    for label, col_name in stats_config:
        cur_val = player.get(col_name, None)
        prev_val = player_prev.get(col_name, None) if player_prev is not None else None
        
        cur_str = f"{cur_val:.2f}" if isinstance(cur_val, (int, float)) and not pd.isna(cur_val) else "N/A"
        prev_str = f"{prev_val:.2f}" if isinstance(prev_val, (int, float)) and not pd.isna(prev_val) else "N/A"
        
        if isinstance(cur_val, (int, float)) and isinstance(prev_val, (int, float)) and not pd.isna(cur_val) and not pd.isna(prev_val):
            delta = f"{cur_val - prev_val:+.2f}"
        else:
            delta = "-"
        
        rows.append((label, cur_str, prev_str, delta))
    
    df_evol = pd.DataFrame(rows, columns=["Métrique", season_display, "2024-2025", "Δ"])
    st.dataframe(df_evol, hide_index=True, use_container_width=True, height=350)

with col_top_right:
    st.subheader(f"🎯 Radar tactique")
    
    # Métriques radar par poste
    RADAR_METRICS_BY_POSITION = {
        "CB": ["int_p90_adj_z", "tkl_won_p90_adj_z", "us_xgbuildup_p90_adj_z", "us_xgchain_p90_adj_z", "fls_committed_p90_adj_z"],
        "FB_L": ["crs_p90_adj_z", "ast_p90_adj_z", "tkl_won_p90_adj_z", "int_p90_adj_z", "us_xa_p90_adj_z"],
        "FB_R": ["crs_p90_adj_z", "ast_p90_adj_z", "tkl_won_p90_adj_z", "int_p90_adj_z", "us_xa_p90_adj_z"],
        "DM": ["int_p90_adj_z", "tkl_won_p90_adj_z", "fls_committed_p90_adj_z", "us_xgbuildup_p90_adj_z", "us_xgchain_p90_adj_z"],
        "CM": ["ast_p90_adj_z", "us_xa_p90_adj_z", "us_kp_p90_adj_z", "int_p90_adj_z", "us_xgbuildup_p90_adj_z"],
        "AM": ["us_kp_p90_adj_z", "us_xa_p90_adj_z", "ast_p90_adj_z", "us_xg_p90_adj_z", "us_shots_p90_adj_z"],
        "W_L": ["gls_p90_adj_z", "us_xg_p90_adj_z", "us_kp_p90_adj_z", "us_xa_p90_adj_z", "fls_drawn_p90_adj_z"],
        "W_R": ["gls_p90_adj_z", "us_xg_p90_adj_z", "us_kp_p90_adj_z", "us_xa_p90_adj_z", "fls_drawn_p90_adj_z"],
        "ST": ["gls_p90_adj_z", "us_xg_p90_adj_z", "us_shots_p90_adj_z", "us_xa_p90_adj_z", "fls_drawn_p90_adj_z"],
    }
    metrics_radar = RADAR_METRICS_BY_POSITION.get(poste, ["us_xg_p90_adj_z", "us_xa_p90_adj_z", "ast_p90_adj_z"])
    
    # Radar overlay
    def z_to_score(z):
        return max(5, min(95, 50 + z * 15))
    
    fig_radar = go.Figure()
    
    # Trace saison courante
    values_cur = [z_to_score(player.get(m, 0)) if m in player.index else 50 for m in metrics_radar]
    labels_cur = [get_metric_label(m) for m in metrics_radar]
    values_cur.append(values_cur[0])
    labels_cur.append(labels_cur[0])
    
    fig_radar.add_trace(go.Scatterpolar(
        r=values_cur,
        theta=labels_cur,
        fill="toself",
        name=f"{season_display}",
        line=dict(color="#4ade80", width=2),
        fillcolor="rgba(74, 222, 128, 0.2)",
    ))
    
    # Trace saison précédente si dispo
    if player_prev is not None:
        values_prev = [z_to_score(player_prev.get(m, 0)) if m in player_prev.index else 50 for m in metrics_radar]
        values_prev.append(values_prev[0])
        
        fig_radar.add_trace(go.Scatterpolar(
            r=values_prev,
            theta=labels_cur,
            fill="toself",
            name="2024-2025",
            line=dict(color="#60a5fa", width=2),
            fillcolor="rgba(96, 165, 250, 0.15)",
        ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=True, tickfont=dict(size=10, color="white"),
                            gridcolor="rgba(255,255,255,0.1)"),
            angularaxis=dict(tickfont=dict(size=11, color="white"), gridcolor="rgba(255,255,255,0.15)"),
            bgcolor="#0e1117",
        ),
        paper_bgcolor="#0e1117",
        font=dict(color="white"),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        height=400,
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)

# --- LIGNE 2 : Bas gauche (évolution VALOR) + Bas droite (Similar Players) ---
col_bot_left, col_bot_right = st.columns([1, 1])

with col_bot_left:
    st.subheader("📈 Évolution VALOR vs médian poste/ligue")
    
    # Récupérer VALOR médian pour ce poste dans cette ligue par saison
    seasons_data = []
    for s_slug in ["2024_2025", "2025_2026"]:
        try:
            df_s = load_valor_data(league_slug, s_slug)
            median_valor = df_s[df_s["valor_position_12"] == poste]["VALOR"].median()
            player_valor = None
            match = df_s[df_s["Player"] == player_name]
            if len(match) > 0:
                player_valor = match.iloc[0]["VALOR"]
            seasons_data.append({
                "Saison": SEASONS[s_slug]["display"],
                "Joueur": player_valor,
                f"Médian {poste} ({league_display})": median_valor,
            })
        except Exception:
            pass
    
    df_evol_valor = pd.DataFrame(seasons_data)
    
    if len(df_evol_valor) > 0:
        fig_evol = go.Figure()
        
        # Ligne joueur
        fig_evol.add_trace(go.Scatter(
            x=df_evol_valor["Saison"], y=df_evol_valor["Joueur"],
            mode="lines+markers",
            name=player_name,
            line=dict(color="#4ade80", width=3),
            marker=dict(size=14),
        ))
        
        # Ligne médian
        median_col = f"Médian {poste} ({league_display})"
        fig_evol.add_trace(go.Scatter(
            x=df_evol_valor["Saison"], y=df_evol_valor[median_col],
            mode="lines+markers",
            name=f"Médian {get_position_label(poste)}",
            line=dict(color="#94a3b8", width=2, dash="dash"),
            marker=dict(size=10),
        ))
        
        fig_evol.update_layout(
            template="plotly_dark",
            plot_bgcolor="#0e1117",
            paper_bgcolor="#0e1117",
            font=dict(color="white"),
            xaxis_title="Saison",
            yaxis_title="VALOR",
            yaxis=dict(range=[30, 100], gridcolor="rgba(255,255,255,0.1)"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
            height=400,
        )
        st.plotly_chart(fig_evol, use_container_width=True)
    else:
        st.info("Pas assez de données historiques pour ce joueur.")

with col_bot_right:
    st.subheader("🎯 Joueurs au profil similaire")
    st.caption(f"Big 5 · {season_display}")
    
    # Charger les 5 ligues pour la saison courante
    df_all = load_all_leagues_season(season_slug)
    
    if len(df_all) == 0:
        st.info("Pas de données Big 5 pour cette saison.")
    else:
        # Filtrer sur le même poste
        df_pool = df_all[df_all["valor_position_12"] == poste].copy()
        df_pool = df_pool[df_pool["Player"] != player_name]  # exclure le joueur lui-même
        
        # Métriques z-scores pour distance
        SIMILARITY_METRICS = {
            "CB": ["int_p90_adj_z", "tkl_won_p90_adj_z", "us_xgbuildup_p90_adj_z", "us_xgchain_p90_adj_z", "fls_committed_p90_adj_z"],
            "FB_L": ["crs_p90_adj_z", "ast_p90_adj_z", "tkl_won_p90_adj_z", "int_p90_adj_z", "us_xa_p90_adj_z", "fls_drawn_p90_adj_z"],
            "FB_R": ["crs_p90_adj_z", "ast_p90_adj_z", "tkl_won_p90_adj_z", "int_p90_adj_z", "us_xa_p90_adj_z", "fls_drawn_p90_adj_z"],
            "DM": ["int_p90_adj_z", "tkl_won_p90_adj_z", "fls_committed_p90_adj_z", "us_xgbuildup_p90_adj_z", "us_xgchain_p90_adj_z"],
            "CM": ["ast_p90_adj_z", "us_xa_p90_adj_z", "us_kp_p90_adj_z", "int_p90_adj_z", "us_xgbuildup_p90_adj_z"],
            "AM": ["us_kp_p90_adj_z", "us_xa_p90_adj_z", "ast_p90_adj_z", "us_xg_p90_adj_z", "us_shots_p90_adj_z"],
            "W_L": ["us_gls_p90_adj_z", "us_xg_p90_adj_z", "us_kp_p90_adj_z", "us_xa_p90_adj_z", "fls_drawn_p90_adj_z", "crs_p90_adj_z"],
            "W_R": ["us_gls_p90_adj_z", "us_xg_p90_adj_z", "us_kp_p90_adj_z", "us_xa_p90_adj_z", "fls_drawn_p90_adj_z", "crs_p90_adj_z"],
            "ST": ["gls_p90_adj_z", "us_xg_p90_adj_z", "us_shots_p90_adj_z", "us_xa_p90_adj_z", "fls_drawn_p90_adj_z"],
        }
        sim_metrics_all = SIMILARITY_METRICS.get(poste, ["us_xg_p90_adj_z", "us_xa_p90_adj_z", "ast_p90_adj_z"])
        
        # Filtre les colonnes qui existent réellement dans le dataset
        sim_metrics = [m for m in sim_metrics_all if m in df_pool.columns]
        
        if len(sim_metrics) == 0:
            st.info(f"Pas de métriques de similarité disponibles pour le poste {poste}.")
        else:
            # Vecteur du joueur cible
            player_vec = np.array([player.get(m, 0) if not pd.isna(player.get(m, 0)) else 0 for m in sim_metrics])
            
            # Vecteurs des candidats
            pool_matrix = df_pool[sim_metrics].fillna(0).to_numpy()
        
            # Distances euclidiennes
            distances = np.linalg.norm(pool_matrix - player_vec, axis=1)
        
            # Similarité (échelle 0-100)
            # Distance moyenne comme référence pour normaliser
            scale = np.percentile(distances, 25) if len(distances) > 0 else 1.0
            similarities = 100 * np.exp(-distances / max(scale, 0.5))
        
            df_pool["__distance"] = distances
            df_pool["__similarity"] = similarities.round(0).astype(int)
        
            # Top 10 les plus similaires
            top_similar = df_pool.nsmallest(10, "__distance")[
                ["Player", "Squad", "__league_display", "VALOR", "__similarity"]
                ].copy()
            top_similar.columns = ["Joueur", "Club", "Ligue", "VALOR", "Sim %"]
            top_similar["VALOR"] = top_similar["VALOR"].round(1)
        
            st.dataframe(top_similar, hide_index=True, use_container_width=True, height=400)
        
            st.caption("💡 Similarité calculée par distance euclidienne sur les z-scores tactiques normalisés du poste.")