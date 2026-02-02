"""Dash 应用的图表组件。"""

from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd

from config.settings import load_series_config


def get_series_colors() -> dict[str, str]:
    """获取系列的颜色映射。
    
    Returns:
        系列 ID 到颜色的字典映射
    """
    series_config = load_series_config()
    return {s["id"]: s["color"] for s in series_config}


def get_series_names() -> dict[str, str]:
    """获取系列的名称映射。
    
    Returns:
        系列 ID 到显示名称的字典映射
    """
    series_config = load_series_config()
    return {s["id"]: s["name"] for s in series_config}


def create_chart_figure(
    data: dict[str, pd.DataFrame],
    display_mode: str = "absolute"
) -> go.Figure:
    """从数据创建 Plotly 图表。
    
    Args:
        data: 系列 ID 到包含 'date' 和 'value' 列的 DataFrame 的字典映射
        display_mode: 'absolute' 或 'scale'
        
    Returns:
        Plotly Figure 对象
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
    
    # 配置布局
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
    
    # 启用缩放和平移
    fig.update_xaxes(fixedrange=False)
    fig.update_yaxes(fixedrange=False)
    
    return fig


def create_empty_figure() -> go.Figure:
    """创建带有占位消息的空图表。
    
    Returns:
        Plotly Figure 对象
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
    """为 Dash 布局创建图表组件。
    
    Returns:
        包含图表的 Div
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
