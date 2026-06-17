"""Classement VALOR complet avec filtres."""
import streamlit as st
from utils.data_loader import load_valor_data, get_position_label


st.set_page_config(page_title="Classement — VALOR", page_icon="📊", layout="wide")

df = load_valor_data()

st.title("📊 Classement complet")
st.markdown(f"**{len(df)} joueurs** notes — Ligue 1 2024-2025")

# --- Filtres ---
st.sidebar.header("Filtres")

# Filtre par poste
postes_dispo = sorted(df["valor_position_12"].unique())
postes_select = st.sidebar.multiselect(
    "Poste",
    options=postes_dispo,
    default=postes_dispo,
    format_func=lambda x: f"{x} ({get_position_label(x)})",
)

# Filtre par equipe
equipes_dispo = sorted(df["Squad"].unique())
equipes_select = st.sidebar.multiselect(
    "Equipe",
    options=equipes_dispo,
    default=equipes_dispo,
)

# Filtre minutes
min_minutes = st.sidebar.slider(
    "Minutes minimum (club principal)",
    min_value=int(df["PlayingTime_Min"].min()),
    max_value=int(df["PlayingTime_Min"].max()),
    value=int(df["PlayingTime_Min"].min()),
    step=100,
)

# Filtre age
ages_dispo = df["Age"].dropna()
if len(ages_dispo) > 0:
    age_min, age_max = int(ages_dispo.min()), int(ages_dispo.max())
    age_range = st.sidebar.slider(
        "Tranche d'age",
        min_value=age_min,
        max_value=age_max,
        value=(age_min, age_max),
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

st.caption("Astuce : utilise les filtres dans la barre laterale pour affiner.")