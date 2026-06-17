"""Chart utilities for VALOR."""
import plotly.graph_objects as go
from .data_loader import get_metric_label


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
        line=dict(color="#1e3a8a"),
        fillcolor="rgba(30, 58, 138, 0.3)",
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=True, tickfont=dict(size=10)),
            angularaxis=dict(tickfont=dict(size=11)),
        ),
        title=title,
        showlegend=False,
        height=500,
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
        name=df_row1["Player"], line=dict(color="#1e3a8a"),
        fillcolor="rgba(30, 58, 138, 0.3)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=values2, theta=labels_closed, fill="toself",
        name=df_row2["Player"], line=dict(color="#dc2626"),
        fillcolor="rgba(220, 38, 38, 0.3)",
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=True, tickfont=dict(size=10)),
            angularaxis=dict(tickfont=dict(size=11)),
        ),
        showlegend=True,
        height=550,
    )
    return fig