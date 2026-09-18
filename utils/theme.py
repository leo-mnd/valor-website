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

    a[data-testid="stTopNavLink"] {
        border-radius: 8px 8px 0 0 !important;
        border-bottom: 2px solid transparent;
        transition: background 0.15s ease, border-color 0.15s ease;
    }
    a[data-testid="stTopNavLink"][aria-current="page"] {
        background: rgba(74, 222, 128, 0.12) !important;
        border-bottom: 2px solid #4ade80;
    }
    a[data-testid="stTopNavLink"]:not([aria-current="page"]):hover {
        background: rgba(255, 255, 255, 0.06) !important;
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


PITCH_POSITIONS = [
    {"code": "ST", "x": 50, "y": 9, "matches": ["ST"]},
    {"code": "AM", "x": 50, "y": 27, "matches": ["AM"]},
    {"code": "W_L", "x": 13, "y": 43, "matches": ["W_L", "W"]},
    {"code": "W_R", "x": 87, "y": 43, "matches": ["W_R", "W"]},
    {"code": "M_L", "x": 26, "y": 58, "matches": ["M_L"]},
    {"code": "CM", "x": 50, "y": 58, "matches": ["CM"]},
    {"code": "M_R", "x": 74, "y": 58, "matches": ["M_R"]},
    {"code": "DM", "x": 50, "y": 76, "matches": ["DM"]},
    {"code": "FB_L", "x": 13, "y": 92, "matches": ["FB_L", "FB"]},
    {"code": "FB_R", "x": 87, "y": 92, "matches": ["FB_R", "FB"]},
    {"code": "CB", "x": 38, "y": 104, "matches": ["CB"]},
    {"code": "CB", "x": 62, "y": 104, "matches": ["CB"]},
]

PITCH_ACTIVE_FILL = "#4ade80"
PITCH_ACTIVE_STROKE = "#166534"
PITCH_ACTIVE_TEXT = "#0e1117"
PITCH_INACTIVE_FILL = "#333947"
PITCH_INACTIVE_STROKE = "#4b5262"
PITCH_INACTIVE_TEXT = "#aab2c0"


def render_position_pitch(selected_codes):
    """Mini terrain SVG : 12 points pour les 13 postes VALOR (CB/W/FB génériques
    allument leurs 2 côtés). Construit en une seule chaîne sans saut de ligne pour
    éviter le piège CommonMark documenté dans render_hero_row.
    """
    selected = set(selected_codes)
    dots = []
    for pos in PITCH_POSITIONS:
        active = any(m in selected for m in pos["matches"])
        fill = PITCH_ACTIVE_FILL if active else PITCH_INACTIVE_FILL
        stroke = PITCH_ACTIVE_STROKE if active else PITCH_INACTIVE_STROKE
        text_fill = PITCH_ACTIVE_TEXT if active else PITCH_INACTIVE_TEXT
        dots.append(
            f'<circle cx="{pos["x"]}" cy="{pos["y"]}" r="6.6" fill="{fill}" stroke="{stroke}" stroke-width="0.9"></circle>'
            f'<text x="{pos["x"]}" y="{pos["y"]}" text-anchor="middle" dominant-baseline="central" '
            f'font-size="5" font-weight="700" fill="{text_fill}">{pos["code"]}</text>'
        )
    svg = (
        '<svg width="100%" viewBox="0 0 100 120" style="max-width:170px;display:block;margin:0 auto;">'
        '<rect x="2" y="2" width="96" height="116" rx="3" fill="#132a1e" stroke="rgba(255,255,255,0.35)" stroke-width="0.8"></rect>'
        '<line x1="2" y1="60" x2="98" y2="60" stroke="rgba(255,255,255,0.28)" stroke-width="0.6"></line>'
        '<circle cx="50" cy="60" r="11" fill="none" stroke="rgba(255,255,255,0.28)" stroke-width="0.6"></circle>'
        '<circle cx="50" cy="60" r="0.9" fill="rgba(255,255,255,0.28)"></circle>'
        '<rect x="32" y="2" width="36" height="11" fill="none" stroke="rgba(255,255,255,0.28)" stroke-width="0.6"></rect>'
        '<rect x="42" y="2" width="16" height="4.5" fill="none" stroke="rgba(255,255,255,0.28)" stroke-width="0.6"></rect>'
        '<rect x="32" y="107" width="36" height="11" fill="none" stroke="rgba(255,255,255,0.28)" stroke-width="0.6"></rect>'
        '<rect x="42" y="113.5" width="16" height="4.5" fill="none" stroke="rgba(255,255,255,0.28)" stroke-width="0.6"></rect>'
        + "".join(dots) +
        "</svg>"
    )
    st.markdown(svg, unsafe_allow_html=True)


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
