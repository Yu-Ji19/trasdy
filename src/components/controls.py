"""Dash 应用的控制面板组件。"""

from dash import html, dcc
from config.settings import load_series_config


def create_time_range_buttons() -> html.Div:
    """创建时间范围选择按钮。
    
    Returns:
        包含时间范围选择按钮组的 Div
    """
    buttons = [
        {"label": "6个月", "value": "6m"},
        {"label": "1年", "value": "1y"},
        {"label": "3年", "value": "3y"},
        {"label": "5年", "value": "5y"},
        {"label": "全部", "value": "all"},
    ]
    
    return html.Div([
        html.Label("时间范围:", style={"fontWeight": "bold", "marginRight": "10px"}),
        dcc.RadioItems(
            id="time-range",
            options=buttons,
            value="1y",
            inline=True,
            style={"display": "inline-block"},
            inputStyle={"marginRight": "5px"},
            labelStyle={"marginRight": "15px"}
        )
    ], style={"marginBottom": "15px"})


def create_display_mode_toggle() -> html.Div:
    """创建显示模式切换（绝对值 vs 归一化）。
    
    Returns:
        包含显示模式单选按钮的 Div
    """
    modes = [
        {"label": "绝对值", "value": "absolute"},
        {"label": "Scale (归一化)", "value": "scale"},
    ]
    
    return html.Div([
        html.Label("显示模式:", style={"fontWeight": "bold", "marginRight": "10px"}),
        dcc.RadioItems(
            id="display-mode",
            options=modes,
            value="absolute",
            inline=True,
            style={"display": "inline-block"},
            inputStyle={"marginRight": "5px"},
            labelStyle={"marginRight": "15px"}
        )
    ], style={"marginBottom": "15px"})


def create_series_checklist() -> html.Div:
    """创建系列选择复选框列表。
    
    Returns:
        包含系列选择复选框的 Div
    """
    series_config = load_series_config()
    
    options = [
        {"label": s["name"], "value": s["id"]} 
        for s in series_config
    ]
    
    # 默认选中所有系列
    default_values = [s["id"] for s in series_config]
    
    return html.Div([
        html.Label("数据系列:", style={"fontWeight": "bold", "marginBottom": "5px", "display": "block"}),
        dcc.Checklist(
            id="series-selection",
            options=options,
            value=default_values,
            style={"display": "flex", "flexWrap": "wrap", "gap": "10px"},
            inputStyle={"marginRight": "5px"},
            labelStyle={"marginRight": "15px"}
        )
    ], style={"marginBottom": "15px"})


def create_refresh_button() -> html.Div:
    """创建数据刷新按钮和状态显示。
    
    Returns:
        包含刷新按钮和状态文本的 Div
    """
    return html.Div([
        html.Button(
            "更新数据",
            id="refresh-button",
            n_clicks=0,
            style={
                "padding": "10px 20px",
                "backgroundColor": "#4CAF50",
                "color": "white",
                "border": "none",
                "borderRadius": "4px",
                "cursor": "pointer",
                "marginRight": "15px"
            }
        ),
        html.Span(id="refresh-status", style={"color": "#666"})
    ], style={"marginTop": "15px"})


def create_control_panel() -> html.Div:
    """创建完整的控制面板。
    
    Returns:
        包含所有控制组件的 Div
    """
    return html.Div([
        html.H3("控制面板", style={"marginTop": "0", "marginBottom": "20px"}),
        create_time_range_buttons(),
        create_display_mode_toggle(),
        create_series_checklist(),
        create_refresh_button(),
    ], style={
        "padding": "20px",
        "backgroundColor": "#f5f5f5",
        "borderRadius": "8px",
        "marginBottom": "20px"
    })
