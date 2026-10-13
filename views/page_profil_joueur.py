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


st.title("🎯 Profil joueur")

# --- Sélecteurs ---
col_league, col_season = st.columns([3, 1])
with col_league:
    league_slug = league_selector(default="ligue1", key="profil_league")
with col_season:
    season_slug = season_selector(default="2025_2026", key="profil_season")
league_display = LEAGUES[league_slug]["display"]
season_display = SEASONS[season_slug]["display"]

df = load_valor_data(league_slug, season_slug)

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

# --- COMPRENDRE SON VALOR : descriptif + points forts / points faibles ---
st.subheader("🧭 Comprendre son VALOR")
st.caption(
    f"VALOR compare {player_name} aux autres {get_position_label(poste).lower()}s du Big 5 "
    "sur un ensemble de métriques offensives et défensives ajustées par la force du "
    "calendrier. 50 = médiane du poste, 100 = meilleur profil statistique possible."
)

has_data = "valor_strength_metric" in player.index

strength_metric = player.get("valor_strength_metric")
strength_pct = player.get("valor_strength_pct")
weakness_metric = player.get("valor_weakness_metric")
weakness_pct = player.get("valor_weakness_pct")
has_strength = strength_metric is not None and pd.notna(strength_metric)
has_weakness = weakness_metric is not None and pd.notna(weakness_metric)

if has_data:
    col_strengths, col_weaknesses = st.columns(2)
    with col_strengths:
        st.markdown("**💪 Point fort**")
        if has_strength:
            st.markdown(f"- {get_metric_label(strength_metric)} — {strength_pct:.0f}e percentile du poste")
        else:
            st.caption("Rien ne se détache nettement (aucune métrique au-dessus du 70e percentile du poste).")
    with col_weaknesses:
        st.markdown("**⚠️ Point faible**")
        if has_weakness:
            st.markdown(f"- {get_metric_label(weakness_metric)} — {weakness_pct:.0f}e percentile du poste")
        else:
            st.caption("Profil solide partout : même son point le moins fort reste dans le haut du poste (70e percentile ou plus).")
    st.caption(
        "Classé par contribution réelle au score (métrique × poids dans la grille du poste), "
        "affiché seulement si le point fort dépasse le 70e percentile du poste, ou si le point "
        "faible reste sous ce seuil."
    )
else:
    st.info("Détail point fort / point faible pas encore disponible pour cette saison (données à régénérer avec le pipeline à jour).")

st.markdown("---")

# --- Charger la saison précédente pour évolution ---
SEASON_KEYS = list(SEASONS.keys())
_season_idx = SEASON_KEYS.index(season_slug)
prev_season_slug = SEASON_KEYS[_season_idx - 1] if _season_idx > 0 else None
prev_season_display = SEASONS[prev_season_slug]["display"] if prev_season_slug else "N/A"
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
    
    df_evol = pd.DataFrame(rows, columns=["Métrique", season_display, prev_season_display, "Δ"])
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
            name=prev_season_display,
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

# --- LIGNE 2 : Évolution VALOR sur 5 saisons (pleine largeur, card stylée) ---
st.markdown("<br>", unsafe_allow_html=True)

# Pour chaque saison, on cherche le joueur dans les 5 ligues (pas que la
# ligue sélectionnée) pour ne pas perdre le fil en cas de transfert Big 5.
# Le médian de référence, lui, reste fixé sur le poste/ligue actuels du
# joueur : c'est l'étalon qui ne bouge pas, pour juger l'évolution dans un
# cadre stable même si le joueur a changé de club/championnat entre-temps.
seasons_data = []
for s_slug in SEASON_KEYS:
    try:
        df_all_s = load_all_leagues_season(s_slug)
        if len(df_all_s) == 0:
            continue
        df_league_s = df_all_s[df_all_s["__league_slug"] == league_slug]
        median_valor = df_league_s[df_league_s["valor_position_12"] == poste]["VALOR"].median()

        match = df_all_s[df_all_s["Player"] == player_name]
        player_valor, player_club, player_league = None, None, None
        if len(match) > 0:
            row = match.iloc[0]
            player_valor = row["VALOR"]
            player_club = row["Squad"]
            player_league = row["__league_display"]

        seasons_data.append({
            "Saison": SEASONS[s_slug]["display"],
            "Joueur": player_valor,
            "Club": player_club,
            "Ligue": player_league,
            f"Médian {poste} ({league_display})": median_valor,
        })
    except Exception:
        pass

df_evol_valor = pd.DataFrame(seasons_data)
median_col = f"Médian {poste} ({league_display})"

with st.container(border=True):
    # Marqueur invisible : seul moyen fiable de cibler CSS cette card précise
    # (st.container(border=True) ne pose pas de classe dédiée par défaut).
    delta_badge = ""
    if player_prev is not None:
        delta_val = float(player["VALOR"] - player_prev["VALOR"])
        if delta_val > 0.05:
            badge_class, arrow = "valor-badge-up", "▲"
        elif delta_val < -0.05:
            badge_class, arrow = "valor-badge-down", "▼"
        else:
            badge_class, arrow = "valor-badge-flat", "▬"
        delta_badge = (
            f'<span class="valor-badge {badge_class}">{arrow} {delta_val:+.1f} pts '
            f'vs {prev_season_display}</span>'
        )
    st.markdown(
        '<div class="valor-chart-card-marker" style="display:flex;align-items:center;'
        f'gap:12px;flex-wrap:wrap;padding:10px 6px 0 6px;">'
        f'<span class="valor-section-title">📈 Évolution du VALOR sur 5 saisons</span>'
        f'{delta_badge}</div>',
        unsafe_allow_html=True,
    )

    if len(df_evol_valor) > 0 and df_evol_valor["Joueur"].notna().sum() > 0:
        # Repère les points "transfert" (changement de championnat suivi vs la
        # dernière saison où le joueur avait des données) pour les distinguer
        # visuellement, et la saison actuellement sélectionnée pour la mettre
        # en avant.
        marker_sizes, marker_symbols, marker_line_widths = [], [], []
        annotations = []
        prev_league = None
        for _, row in df_evol_valor.iterrows():
            is_current = row["Saison"] == season_display
            is_transfer = (
                pd.notna(row["Ligue"]) and prev_league is not None and row["Ligue"] != prev_league
            )
            if pd.notna(row["Ligue"]):
                prev_league = row["Ligue"]

            marker_sizes.append(18 if is_current else 11)
            marker_symbols.append("diamond" if is_transfer else "circle")
            marker_line_widths.append(3 if is_current else 1)
            if is_transfer:
                annotations.append(dict(
                    x=row["Saison"], y=row["Joueur"],
                    text=row["Ligue"].split(" ")[0],
                    showarrow=False, yshift=22,
                    font=dict(size=15),
                ))

        fig_evol = go.Figure()

        # Ligne médian (étalon fixe, en arrière-plan, poste + ligue actuels)
        fig_evol.add_trace(go.Scatter(
            x=df_evol_valor["Saison"], y=df_evol_valor[median_col],
            mode="lines+markers",
            name=f"Médian {get_position_label(poste)} ({league_display})",
            line=dict(color="#94a3b8", width=2, dash="dash", shape="spline", smoothing=0.3),
            marker=dict(size=7, color="#94a3b8"),
            hovertemplate="<b>%{x}</b><br>Médian : %{y:.1f}<extra></extra>",
        ))

        # Ligne joueur : courbe lissée + dégradé sous la courbe + markers
        # agrandis sur la saison en cours / changement de championnat.
        fig_evol.add_trace(go.Scatter(
            x=df_evol_valor["Saison"], y=df_evol_valor["Joueur"],
            mode="lines+markers",
            name=player_name,
            line=dict(color="#4ade80", width=3.5, shape="spline", smoothing=0.3),
            marker=dict(
                size=marker_sizes, symbol=marker_symbols, color="#4ade80",
                line=dict(width=marker_line_widths, color="#0e1117"),
            ),
            fill="tozeroy",
            fillgradient=dict(
                type="vertical",
                colorscale=[[0, "rgba(74,222,128,0.32)"], [1, "rgba(74,222,128,0.0)"]],
            ),
            customdata=df_evol_valor[["Club", "Ligue"]],
            hovertemplate="<b>%{x}</b><br>VALOR : %{y:.1f}<br>%{customdata[0]} (%{customdata[1]})<extra></extra>",
        ))

        fig_evol.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0", family="Geist Sans, sans-serif", size=13),
            yaxis_title="VALOR",
            yaxis=dict(range=[30, 100], gridcolor="rgba(255,255,255,0.06)", zeroline=False),
            xaxis=dict(showgrid=False, zeroline=False),
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.22, xanchor="center", x=0.5,
                font=dict(size=12), bgcolor="rgba(0,0,0,0)",
            ),
            hoverlabel=dict(
                bgcolor="#161a23", bordercolor="rgba(255,255,255,0.12)",
                font=dict(family="Geist Sans, sans-serif", size=13, color="#fafafa"),
            ),
            annotations=annotations,
            height=420,
            margin=dict(t=30, b=10, l=10, r=10),
        )
        st.plotly_chart(fig_evol, use_container_width=True)
        if df_evol_valor["Joueur"].isna().any():
            st.caption("Point manquant : joueur absent du Big 5 cette saison-là (hors championnat suivi, blessure longue, etc.).")
    else:
        st.info("Pas assez de données historiques pour ce joueur.")

st.markdown("---")

# --- LIGNE 3 : Joueurs au profil similaire ---
col_bot_right = st.container()
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