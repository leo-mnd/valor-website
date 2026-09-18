"""Theme utilities: CSS injection, position colors, hero cards (dark theme)."""
import html as html_lib
import streamlit as st

POSITION_COLORS = {
    "GK": "#94a3b8",
    "CB": "#60a5fa",
    "FB_L": "#38bdf8", "FB_R": "#38bdf8",
    "M_L": "#38bdf8", "M_R": "#38bdf8",
    "DM": "#a78bfa",
    "CM": "#c084fc",
    "AM": "#f472b6",
    "W_L": "#fb923c", "W_R": "#fb923c",
    "ST": "#4ade80",
}

# Layout partagé pour les figures Plotly (fond sombre façon page scatter)
DARK_PLOTLY_LAYOUT = dict(
    plot_bgcolor="#0e1117",
    paper_bgcolor="#0e1117",
    font=dict(color="white"),
)


def get_position_color(pos_code: str) -> str:
    """Couleur associée à un poste, pour badges/avatars."""
    return POSITION_COLORS.get(pos_code, "#4ade80")


def get_initials(name: str) -> str:
    """Initiales d'un joueur pour l'avatar stylisé (ex: 'Ousmane Dembélé' -> 'OD')."""
    parts = [p for p in name.strip().split(" ") if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def inject_css():
    """Injecte le CSS dark theme (cards, animations) commun à toutes les pages."""
    st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #161a23, #1c212c);
        border: 1px solid rgba(255,255,255,0.08);
        padding: 16px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(74, 222, 128, 0.15);
    }

    .valor-hero-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0;
        background: linear-gradient(90deg, #4ade80, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .valor-hero-subtitle {
        color: #94a3b8;
        font-size: 15px;
        margin-top: 0;
        margin-bottom: 12px;
    }

    .valor-hero-row {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
        margin: 8px 0 24px 0;
    }
    .valor-hero-card {
        flex: 1 1 220px;
        background: linear-gradient(160deg, #161a23 0%, #10131a 100%);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 16px;
        padding: 20px;
        position: relative;
        overflow: hidden;
        opacity: 0;
        animation: valorFadeUp 0.6s ease forwards;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    }
    .valor-hero-card:hover {
        transform: translateY(-6px) scale(1.02);
        border-color: rgba(255,255,255,0.2);
        box-shadow: 0 12px 28px rgba(0,0,0,0.45);
    }
    .valor-hero-rank {
        position: absolute;
        top: 14px;
        right: 16px;
        font-size: 13px;
        font-weight: 700;
        color: #64748b;
    }
    .valor-avatar {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 20px;
        color: #0e1117;
        margin-bottom: 14px;
        box-shadow: 0 0 0 3px rgba(255,255,255,0.06);
    }
    .valor-hero-name { font-size: 16px; font-weight: 700; color: #fafafa; margin: 0 0 2px 0; }
    .valor-hero-sub { font-size: 12.5px; color: #94a3b8; margin: 0 0 14px 0; }
    .valor-hero-score { font-size: 28px; font-weight: 800; color: #fafafa; margin: 0; }
    .valor-hero-bar-bg {
        width: 100%; height: 6px; border-radius: 3px;
        background: rgba(255,255,255,0.08);
        margin-top: 8px; overflow: hidden;
    }
    .valor-hero-bar-fill { height: 100%; border-radius: 3px; }

    @keyframes valorFadeUp {
        from { opacity: 0; transform: translateY(14px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)


def render_hero_row(df_top, get_position_label_fn):
    """Affiche une rangée de cards joueurs (avatar initiales + couleur poste, VALOR, barre).

    Construit en HTML compact sur une seule ligne par card : une ligne vide entre deux
    blocs <div> ferme prématurément le bloc HTML brut de Streamlit/CommonMark (contrairement
    à <style>, qui est un cas spécial insensible aux lignes vides), ce qui ferait retomber
    les cards suivantes en texte échappé au lieu d'être rendues.
    """
    parts = ['<div class="valor-hero-row">']
    for i, (_, row) in enumerate(df_top.iterrows()):
        pos = row["valor_position_12"]
        color = get_position_color(pos)
        initials = get_initials(str(row["Player"]))
        valor = float(row["VALOR"])
        name = html_lib.escape(str(row["Player"]))
        squad = html_lib.escape(str(row["Squad"]))
        pos_label = html_lib.escape(get_position_label_fn(pos))
        parts.append(
            f'<div class="valor-hero-card" style="animation-delay:{i * 0.08}s;">'
            f'<div class="valor-hero-rank">#{i + 1}</div>'
            f'<div class="valor-avatar" style="background:{color};">{initials}</div>'
            f'<p class="valor-hero-name">{name}</p>'
            f'<p class="valor-hero-sub">{squad} · {pos_label}</p>'
            f'<p class="valor-hero-score">{valor:.1f}</p>'
            f'<div class="valor-hero-bar-bg">'
            f'<div class="valor-hero-bar-fill" style="width:{min(valor, 100)}%; background:{color};"></div>'
            f'</div>'
            f'</div>'
        )
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)
