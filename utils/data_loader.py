"""Data loading utilities for VALOR."""
import pandas as pd
import streamlit as st
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data"


@st.cache_data
def load_valor_data() -> pd.DataFrame:
    """Charge le DataFrame VALOR principal avec mise en cache."""
    path = DATA_DIR / "valor_ligue1_2024_2025.parquet"
    df = pd.read_parquet(path)
    df = df.sort_values("VALOR", ascending=False).reset_index(drop=True)
    df.insert(0, "Rang", df.index + 1)
    return df


@st.cache_data
def load_team_data() -> pd.DataFrame:
    """Charge les stats équipes."""
    path = DATA_DIR / "team_stats_ligue1_2024_2025.parquet"
    return pd.read_parquet(path)


def get_position_label(p12: str) -> str:
    """Convertit le code poste 12 en label lisible."""
    labels = {
        "GK": "Gardien", "CB": "Défenseur central",
        "FB_L": "Latéral gauche", "FB_R": "Latéral droit",
        "DM": "Milieu défensif", "CM": "Milieu central",
        "M_L": "Milieu gauche", "M_R": "Milieu droit",
        "AM": "Milieu offensif",
        "W_L": "Ailier gauche", "W_R": "Ailier droit",
        "ST": "Attaquant",
    }
    return labels.get(p12, p12)


def get_metric_label(metric: str) -> str:
    """Convertit un nom de colonne z-score en label lisible pour le radar."""
    labels = {
        "gls_p90_adj_z": "Buts",
        "ast_p90_adj_z": "Passes decisives",
        "us_xg_p90_adj_z": "xG (qualite tirs)",
        "us_xa_p90_adj_z": "xA (qualite passes)",
        "us_shots_p90_adj_z": "Tirs",
        "us_kp_p90_adj_z": "Passes cles",
        "us_xgchain_p90_adj_z": "xGChain",
        "us_xgbuildup_p90_adj_z": "xGBuildup",
        "tkl_won_p90_adj_z": "Tacles gagnes",
        "int_p90_adj_z": "Interceptions",
        "crs_p90_adj_z": "Centres",
        "fls_drawn_p90_adj_z": "Fautes provoquees",
    }
    return labels.get(metric, metric)