"""Trasdy MVP - Macro Economic Data Platform.

A Dash-based application for visualizing macroeconomic data from FRED.
"""

from dash import Dash, html, dcc, callback, Output, Input, State
from datetime import datetime

from src.components.controls import create_control_panel
from src.components.chart import create_chart_component, create_chart_figure, create_empty_figure
from src.services.transform import prepare_chart_data
from src.services.data_service import DataService, RefreshMode
from src.repositories.csv_repository import CSVSeriesRepository, JSONMetadataRepository


# Initialize services
series_repo = CSVSeriesRepository()
metadata_repo = JSONMetadataRepository()
data_service = DataService(series_repo, metadata_repo)

# Initialize Dash app
app = Dash(__name__)
app.title = "Trasdy - 宏观经济数据平台"

# Layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Trasdy", style={"margin": "0", "color": "#333"}),
        html.P("宏观经济数据分析平台", style={"margin": "5px 0 0 0", "color": "#666"})
    ], style={
        "padding": "20px",
        "backgroundColor": "white",
        "borderBottom": "1px solid #ddd",
        "marginBottom": "20px"
    }),
    
    # Main content
    html.Div([
        # Control panel
        create_control_panel(),
        
        # Chart area
        create_chart_component(),
        
        # Status bar
        html.Div(id="status-bar", style={
            "padding": "10px",
            "color": "#666",
            "fontSize": "12px",
            "marginTop": "10px"
        })
    ], style={
        "maxWidth": "1200px",
        "margin": "0 auto",
        "padding": "0 20px"
    }),
    
    # Store for data caching
    dcc.Store(id="data-store"),
    
], style={
    "fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    "backgroundColor": "#f0f2f5",
    "minHeight": "100vh"
})


@callback(
    Output("data-store", "data"),
    Input("series-selection", "value"),
    prevent_initial_call=False
)
def load_data(selected_series):
    """Load data for selected series."""
    if not selected_series:
        return {}
    
    try:
        data_dict = data_service.get_series(selected_series)
        # Convert to JSON-serializable format
        result = {}
        for series_id, df in data_dict.items():
            if not df.empty:
                result[series_id] = {
                    "date": [d.isoformat() if hasattr(d, 'isoformat') else str(d) for d in df["date"]],
                    "value": df["value"].tolist()
                }
        return result
    except Exception as e:
        print(f"Error loading data: {e}")
        return {}


@callback(
    Output("main-chart", "figure"),
    Input("data-store", "data"),
    Input("time-range", "value"),
    Input("display-mode", "value"),
    Input("series-selection", "value"),
)
def update_chart(stored_data, time_range, display_mode, selected_series):
    """Update chart based on controls."""
    if not stored_data or not selected_series:
        return create_empty_figure()
    
    import pandas as pd
    
    # Convert stored data back to DataFrames
    data_dict = {}
    for series_id in selected_series:
        if series_id in stored_data:
            series_data = stored_data[series_id]
            df = pd.DataFrame({
                "date": pd.to_datetime(series_data["date"]).dt.date,
                "value": series_data["value"]
            })
            data_dict[series_id] = df
    
    if not data_dict:
        return create_empty_figure()
    
    # Apply transformations
    normalize = (display_mode == "scale")
    prepared_data = prepare_chart_data(data_dict, range_key=time_range, normalize=normalize)
    
    return create_chart_figure(prepared_data, display_mode)


@callback(
    Output("refresh-status", "children"),
    Output("data-store", "data", allow_duplicate=True),
    Input("refresh-button", "n_clicks"),
    State("series-selection", "value"),
    prevent_initial_call=True
)
def refresh_data(n_clicks, selected_series):
    """Refresh data from FRED API."""
    if not n_clicks or not selected_series:
        return "", {}
    
    try:
        # Get all configured series for refresh
        all_series = data_service.get_all_configured_series_ids()
        result = data_service.refresh_data(all_series, mode=RefreshMode.INCREMENTAL)
        
        total_records = sum(result.values())
        timestamp = datetime.now().strftime("%H:%M:%S")
        status = f"已更新 {total_records} 条记录 ({timestamp})"
        
        # Reload data
        data_dict = data_service.get_series(selected_series)
        stored = {}
        for series_id, df in data_dict.items():
            if not df.empty:
                stored[series_id] = {
                    "date": [d.isoformat() if hasattr(d, 'isoformat') else str(d) for d in df["date"]],
                    "value": df["value"].tolist()
                }
        
        return status, stored
    except Exception as e:
        return f"更新失败: {str(e)}", {}


@callback(
    Output("status-bar", "children"),
    Input("data-store", "data"),
    Input("time-range", "value"),
    Input("display-mode", "value"),
)
def update_status(stored_data, time_range, display_mode):
    """Update status bar with current settings."""
    if not stored_data:
        return "请选择数据系列"
    
    series_count = len(stored_data)
    mode_text = "绝对值" if display_mode == "absolute" else "归一化"
    range_map = {"6m": "6个月", "1y": "1年", "3y": "3年", "5y": "5年", "all": "全部"}
    range_text = range_map.get(time_range, time_range)
    
    return f"显示 {series_count} 个系列 | 范围: {range_text} | 模式: {mode_text}"


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
