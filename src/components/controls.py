"""Control panel components for Dash application."""

from dash import html, dcc
from config.settings import load_series_config


def create_time_range_buttons() -> html.Div:
    """Create time range selection buttons.
    
    Returns:
        Div containing button group for time range selection
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
    """Create display mode toggle (absolute vs normalized).
    
    Returns:
        Div containing radio buttons for display mode
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
    """Create series selection checklist.
    
    Returns:
        Div containing checkboxes for series selection
    """
    series_config = load_series_config()
    
    options = [
        {"label": s["name"], "value": s["id"]} 
        for s in series_config
    ]
    
    # Default to all series selected
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
    """Create data refresh button and status display.
    
    Returns:
        Div containing refresh button and status text
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
    """Create the complete control panel.
    
    Returns:
        Div containing all control components
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
