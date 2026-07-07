"""Data loading utilities for VALOR."""
import pandas as pd
import streamlit as st
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data"

# Mapping ligue → slug fichier et nom d'affichage
LEAGUES = {
    "ligue1": {"display": "🇫🇷 Ligue 1", "slug": "ligue1"},
    "premier_league": {"display": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League", "slug": "premier_league"},
    "la_liga": {"display": "🇪🇸 La Liga", "slug": "la_liga"},
    "bundesliga": {"display": "🇩🇪 Bundesliga", "slug": "bundesliga"},
    "serie_a": {"display": "🇮🇹 Serie A", "slug": "serie_a"},
}

LEAGUE_DISPLAY_TO_SLUG = {v["display"]: k for k, v in LEAGUES.items()}

# Mapping saison → slug fichier et nom d'affichage
SEASONS = {
    "2024_2025": {"display": "2024-2025", "slug": "2024_2025"},
    "2025_2026": {"display": "2025-2026", "slug": "2025_2026"},
}

SEASON_DISPLAY_TO_SLUG = {v["display"]: k for k, v in SEASONS.items()}


@st.cache_data
def load_valor_data(league: str = "ligue1", season: str = "2024_2025") -> pd.DataFrame:
    """Charge le DataFrame VALOR pour la ligue et saison données."""
    path = DATA_DIR / f"valor_{league}_{season}.parquet"
    df = pd.read_parquet(path)
    df = df.sort_values("VALOR", ascending=False).reset_index(drop=True)
    if "Rang" not in df.columns:
        df.insert(0, "Rang", df.index + 1)
    return df


@st.cache_data
def load_team_stats(league: str = "ligue1", season: str = "2024_2025") -> pd.DataFrame:
    """Charge les stats équipes pour la ligue et saison données."""
    path = DATA_DIR / f"team_stats_{league}_{season}.parquet"
    return pd.read_parquet(path)


def get_position_label(pos_code: str) -> str:
    """Convertit un code de poste en label lisible."""
    labels = {
        "GK": "Gardien",
        "CB": "Défenseur central",
        "FB_L": "Latéral gauche",
        "FB_R": "Latéral droit",
        "DM": "Milieu défensif",
        "CM": "Milieu central",
        "AM": "Milieu offensif",
        "W_L": "Ailier gauche",
        "W_R": "Ailier droit",
        "ST": "Attaquant",
        "M_L": "Latéral gauche",
        "M_R": "Latéral droit",
    }
    return labels.get(pos_code, pos_code)


def get_metric_label(metric_code: str) -> str:
    """Convertit un code de métrique en label lisible pour affichage."""
    labels = {
        "gls_p90_adj": "Buts /90",
        "us_xg_p90_adj": "xG /90",
        "us_shots_p90_adj": "Tirs /90",
        "ast_p90_adj": "PD /90",
        "us_xa_p90_adj": "xA /90",
        "us_kp_p90_adj": "KP /90",
        "us_xgchain_p90_adj": "xGChain /90",
        "us_xgbuildup_p90_adj": "xGBuildup /90",
        "fls_drawn_p90_adj": "Fautes provoquées /90",
        "tkl_won_p90_adj": "Tacles gagnés /90",
        "int_p90_adj": "Interceptions /90",
        "crs_p90_adj": "Centres /90",
        "gls_p90_adj_z": "Buts /90",
        "us_xg_p90_adj_z": "xG /90",
        "us_shots_p90_adj_z": "Tirs /90",
        "ast_p90_adj_z": "PD /90",
        "us_xa_p90_adj_z": "xA /90",
        "us_kp_p90_adj_z": "KP /90",
        "us_xgchain_p90_adj_z": "xGChain /90",
        "us_xgbuildup_p90_adj_z": "xGBuildup /90",
        "fls_drawn_p90_adj_z": "Fautes provoquées /90",
        "tkl_won_p90_adj_z": "Tacles gagnés /90",
        "int_p90_adj_z": "Interceptions /90",
        "crs_p90_adj_z": "Centres /90",
    }
    return labels.get(metric_code, metric_code)


def league_selector(default: str = "ligue1", key: str = "league_selector") -> str:
    """
    Affiche un sélecteur de ligue dans la sidebar Streamlit.
    Retourne le slug de la ligue sélectionnée.
    """
    league_names = [v["display"] for v in LEAGUES.values()]
    default_display = LEAGUES[default]["display"]
    default_idx = league_names.index(default_display)
    
    selected_display = st.sidebar.selectbox(
        "🏆 Championnat",
        options=league_names,
        index=default_idx,
        key=key,
    )
    return LEAGUE_DISPLAY_TO_SLUG[selected_display]


def season_selector(default: str = "2024_2025", key: str = "season_selector") -> str:
    """
    Affiche un sélecteur de saison dans la sidebar Streamlit.
    Retourne le slug de la saison sélectionnée.
    """
    season_names = [v["display"] for v in SEASONS.values()]
    default_display = SEASONS[default]["display"]
    default_idx = season_names.index(default_display)
    
    selected_display = st.sidebar.selectbox(
        "📅 Saison",
        options=season_names,
        index=default_idx,
        key=key,
    )
    return SEASON_DISPLAY_TO_SLUG[selected_display]