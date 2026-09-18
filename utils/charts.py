"""Chart utilities for VALOR."""
import plotly.graph_objects as go
from .data_loader import get_metric_label
from .theme import DARK_PLOTLY_LAYOUT

POLAR_DARK = dict(
    radialaxis=dict(
        visible=True, range=[0, 100], showticklabels=True,
        tickfont=dict(size=10, color="white"),
        gridcolor="rgba(255,255,255,0.1)",
    ),
    angularaxis=dict(tickfont=dict(size=11, color="white"), gridcolor="rgba(255,255,255,0.15)"),
    bgcolor="#0e1117",
)


def player_radar(df_row, metrics: list, title: str = "") -> go.Figure:
    """Cree un radar des z-scores d'un joueur (transformes en 0-100)."""

    def z_to_score(z):
        return max(5, min(95, 50 + z * 15))

    values = [z_to_score(df_row[m]) if m in df_row.index else 50 for m in metrics]
    labels = [get_metric_label(m) for m in metrics]

    values.append(values[0])
    labels.append(labels[0])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=labels,
        fill="toself",
        name=df_row["Player"],
        line=dict(color="#4ade80"),
        fillcolor="rgba(74, 222, 128, 0.25)",
    ))

    fig.update_layout(
        polar=POLAR_DARK,
        title=title,
        showlegend=False,
        height=500,
        **DARK_PLOTLY_LAYOUT,
    )
    return fig


def comparison_radar(df_row1, df_row2, metrics: list) -> go.Figure:
    """Cree un radar comparant 2 joueurs."""

    def z_to_score(z):
        return max(5, min(95, 50 + z * 15))

    labels = [get_metric_label(m) for m in metrics]
    labels_closed = labels + [labels[0]]

    values1 = [z_to_score(df_row1[m]) if m in df_row1.index else 50 for m in metrics]
    values2 = [z_to_score(df_row2[m]) if m in df_row2.index else 50 for m in metrics]
    values1.append(values1[0])
    values2.append(values2[0])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values1, theta=labels_closed, fill="toself",
        name=df_row1["Player"], line=dict(color="#4ade80"),
        fillcolor="rgba(74, 222, 128, 0.25)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=values2, theta=labels_closed, fill="toself",
        name=df_row2["Player"], line=dict(color="#f472b6"),
        fillcolor="rgba(244, 114, 182, 0.25)",
    ))

    fig.update_layout(
        polar=POLAR_DARK,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(color="white")),
        height=550,
        **DARK_PLOTLY_LAYOUT,
    )
    return fig
