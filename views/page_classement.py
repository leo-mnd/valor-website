"""Classement VALOR complet avec filtres."""
import streamlit as st
from utils.data_loader import (
    load_valor_data, get_position_label,
    league_selector, season_selector, LEAGUES, SEASONS
)
from utils.theme import render_position_pitch


st.title("📊 Classement complet")

col_league, col_season = st.columns([3, 1])
with col_league:
    league_slug = league_selector(default="ligue1", key="classement_league")
with col_season:
    season_slug = season_selector(default="2025_2026", key="classement_season")
league_display = LEAGUES[league_slug]["display"]
season_display = SEASONS[season_slug]["display"]

df = load_valor_data(league_slug, season_slug)
st.markdown(f"**{len(df)} joueurs** notes — {league_display} {season_display}")

# --- Filtres ---
postes_dispo = sorted(df["valor_position_12"].unique())
col_postes, col_pitch = st.columns([4, 1])
with col_postes:
    postes_select = st.segmented_control(
        "Poste",
        options=postes_dispo,
        default=postes_dispo,
        selection_mode="multi",
        key="classement_postes",
    ) or postes_dispo
with col_pitch:
    render_position_pitch(postes_select)

col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
with col_f1:
    equipes_dispo = sorted(df["Squad"].unique())
    equipes_select = st.multiselect(
        "Équipe",
        options=equipes_dispo,
        default=equipes_dispo,
        key="classement_equipes",
    )
with col_f2:
    min_minutes = st.slider(
        "Minutes minimum (club principal)",
        min_value=int(df["PlayingTime_Min"].min()),
        max_value=int(df["PlayingTime_Min"].max()),
        value=int(df["PlayingTime_Min"].min()),
        step=100,
        key="classement_minutes",
    )
with col_f3:
    ages_dispo = df["Age"].dropna()
    if len(ages_dispo) > 0:
        age_min, age_max = int(ages_dispo.min()), int(ages_dispo.max())
        age_range = st.slider(
            "Tranche d'age",
            min_value=age_min,
            max_value=age_max,
            value=(age_min, age_max),
            key="classement_age",
        )
    else:
        age_range = (0, 100)

# --- Application des filtres ---
df_filtered = df[
    (df["valor_position_12"].isin(postes_select)) &
    (df["Squad"].isin(equipes_select)) &
    (df["PlayingTime_Min"] >= min_minutes) &
    (df["Age"].fillna(0).between(age_range[0], age_range[1]))
].copy()

# Rang recalcule sur le filtre
df_filtered = df_filtered.sort_values("VALOR", ascending=False).reset_index(drop=True)
df_filtered["Rang_filtre"] = df_filtered.index + 1

# --- Affichage ---
st.markdown("---")
col1, col2 = st.columns([1, 1])
col1.metric("Joueurs affiches", len(df_filtered))
col2.metric("VALOR moyen", f"{df_filtered['VALOR'].mean():.1f}" if len(df_filtered) > 0 else "—")

st.markdown("---")

# Tableau
display_cols = [
    "Rang_filtre", "Player", "Squad", "valor_position_12",
    "Age", "Nation", "PlayingTime_Min",
    "Performance_Gls", "Performance_Ast", "VALOR",
]
display_cols = [c for c in display_cols if c in df_filtered.columns]

df_display = df_filtered[display_cols].rename(columns={
    "Rang_filtre": "Rang",
    "valor_position_12": "Poste",
    "PlayingTime_Min": "Minutes",
    "Performance_Gls": "Buts",
    "Performance_Ast": "PD",
})

st.dataframe(
    df_display,
    hide_index=True,
    use_container_width=True,
    height=600,
    column_config={
        "VALOR": st.column_config.ProgressColumn(
            "VALOR",
            min_value=0,
            max_value=100,
            format="%.1f",
        ),
    },
)

st.caption("Astuce : utilise les filtres ci-dessus pour affiner.")
