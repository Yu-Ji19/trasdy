"""Trasdy MVP - 宏观经济数据平台

基于 Dash 的宏观经济数据可视化应用，数据来源于 FRED。
"""

from dash import Dash, html, dcc, callback, Output, Input, State
from datetime import datetime

from src.components.controls import create_control_panel
from src.components.chart import create_chart_component, create_chart_figure, create_empty_figure
from src.services.transform import prepare_chart_data
from src.services.data_service import DataService, RefreshMode
from src.repositories.csv_repository import CSVSeriesRepository, JSONMetadataRepository


# 初始化服务
series_repo = CSVSeriesRepository()
metadata_repo = JSONMetadataRepository()
data_service = DataService(series_repo, metadata_repo)

# 初始化 Dash 应用
app = Dash(__name__)
app.title = "Trasdy - 宏观经济数据平台"

# 布局
app.layout = html.Div([
    # 页头
    html.Div([
        html.H1("Trasdy", style={"margin": "0", "color": "#333"}),
        html.P("宏观经济数据分析平台", style={"margin": "5px 0 0 0", "color": "#666"})
    ], style={
        "padding": "20px",
        "backgroundColor": "white",
        "borderBottom": "1px solid #ddd",
        "marginBottom": "20px"
    }),
    
    # 主内容区
    html.Div([
        # 控制面板
        create_control_panel(),
        
        # 图表区域
        create_chart_component(),
        
        # 状态栏
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
    
    # 数据缓存存储
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
    """加载选中的数据系列。"""
    if not selected_series:
        return {}
    
    try:
        data_dict = data_service.get_series(selected_series)
        # 转换为 JSON 可序列化格式
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
    """根据控制选项更新图表。"""
    if not stored_data or not selected_series:
        return create_empty_figure()
    
    import pandas as pd
    
    # 将存储的数据转换回 DataFrame
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
    
    # 应用数据转换
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
    """从 FRED API 刷新数据。"""
    if not n_clicks or not selected_series:
        return "", {}
    
    try:
        # 获取所有配置的系列进行刷新
        all_series = data_service.get_all_configured_series_ids()
        result = data_service.refresh_data(all_series, mode=RefreshMode.INCREMENTAL)
        
        total_records = sum(result.values())
        timestamp = datetime.now().strftime("%H:%M:%S")
        status = f"已更新 {total_records} 条记录 ({timestamp})"
        
        # 重新加载数据
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
    """更新状态栏显示当前设置。"""
    if not stored_data:
        return "请选择数据系列"
    
    series_count = len(stored_data)
    mode_text = "绝对值" if display_mode == "absolute" else "归一化"
    range_map = {"6m": "6个月", "1y": "1年", "3y": "3年", "5y": "5年", "all": "全部"}
    range_text = range_map.get(time_range, time_range)
    
    return f"显示 {series_count} 个系列 | 范围: {range_text} | 模式: {mode_text}"


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
