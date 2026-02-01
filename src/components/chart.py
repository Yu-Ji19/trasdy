"""Chart components for Dash application."""

from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd

from config.settings import load_series_config


def get_series_colors() -> dict[str, str]:
    """Get color mapping for series.
    
    Returns:
        Dictionary mapping series_id to color
    """
    series_config = load_series_config()
    return {s["id"]: s["color"] for s in series_config}


def get_series_names() -> dict[str, str]:
    """Get name mapping for series.
    
    Returns:
        Dictionary mapping series_id to display name
    """
    series_config = load_series_config()
    return {s["id"]: s["name"] for s in series_config}


def create_chart_figure(
    data: dict[str, pd.DataFrame],
    display_mode: str = "absolute"
) -> go.Figure:
    """Create Plotly figure from data.
    
    Args:
        data: Dictionary mapping series_id to DataFrame with 'date' and 'value' columns
        display_mode: 'absolute' or 'scale'
        
    Returns:
        Plotly Figure object
    """
    colors = get_series_colors()
    names = get_series_names()
    
    fig = go.Figure()
    
    for series_id, df in data.items():
        if df.empty:
            continue
        
        color = colors.get(series_id, "#333333")
        name = names.get(series_id, series_id)
        
        fig.add_trace(go.Scatter(
            x=df["date"],
            y=df["value"],
            mode="lines",
            name=name,
            line=dict(color=color, width=2),
            hovertemplate="<b>%{x}</b><br>" + name + ": %{y:.2f}<extra></extra>"
        ))
    
    # Configure layout
    y_title = "值" if display_mode == "absolute" else "归一化值 (起始=100)"
    
    fig.update_layout(
        title=None,
        xaxis=dict(
            title="日期",
            showgrid=True,
            gridcolor="rgba(0,0,0,0.1)",
            rangeslider=dict(visible=False),
        ),
        yaxis=dict(
            title=y_title,
            showgrid=True,
            gridcolor="rgba(0,0,0,0.1)",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        hovermode="x unified",
        margin=dict(l=60, r=20, t=40, b=60),
        height=500,
        plot_bgcolor="white",
    )
    
    # Enable zoom and pan
    fig.update_xaxes(fixedrange=False)
    fig.update_yaxes(fixedrange=False)
    
    return fig


def create_empty_figure() -> go.Figure:
    """Create an empty figure with placeholder message.
    
    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    fig.add_annotation(
        text="选择数据系列以显示图表",
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=16, color="#666")
    )
    fig.update_layout(
        height=500,
        plot_bgcolor="white",
    )
    return fig


def create_chart_component() -> html.Div:
    """Create the chart component for the Dash layout.
    
    Returns:
        Div containing the chart
    """
    return html.Div([
        dcc.Graph(
            id="main-chart",
            figure=create_empty_figure(),
            config={
                "displayModeBar": True,
                "scrollZoom": True,
                "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                "displaylogo": False
            }
        )
    ], style={
        "backgroundColor": "white",
        "borderRadius": "8px",
        "padding": "10px",
        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
    })
