---
task: Build Trasdy MVP - Macro Economic Data Platform
test_command: "python app.py"
---

# Task: Trasdy MVP

基于 Dash + Plotly + CSV 的宏观经济数据分析平台 MVP。

## Requirements

1. 技术栈：Python 3.10+, Dash, Plotly, pandas
2. 数据源：FRED API
3. 存储：CSV 文件
4. 参考设计：MVP_DESIGN.md

---

## Success Criteria

### Phase 0: 前置验证

1. [ ] 创建 `scripts/test_fred_api.py` 脚本，读取 `FRED_API_KEY` 文件，调用 FRED API 拉取 SP500 最近 10 条数据并打印
   - 验收：运行 `python scripts/test_fred_api.py` 输出日期和数值，无报错

### Phase 1: 环境搭建

2. [x] 创建项目目录结构：`src/adapters/`, `src/repositories/`, `src/services/`, `src/components/`, `config/`, `data/raw/`，每个目录下创建 `__init__.py`
   - 验收：所有目录存在且包含 `__init__.py`

3. [x] 创建 `requirements.txt`，包含 dash, plotly, pandas, requests, pyyaml
   - 验收：`pip install -r requirements.txt` 安装成功

4. [ ] 创建 `config/settings.py`，实现 `get_api_key()` 函数读取项目根目录的 `FRED_API_KEY` 文件内容
   - 验收：`python -c "from config.settings import get_api_key; print(get_api_key())"` 输出 API Key
   - 注：settings.py 已创建，等待 FRED_API_KEY 文件填入 API Key

5. [x] 创建 `config/series_config.yaml`，配置 6 个数据系列：SP500, DFEDTARU, DFEDTARL, DGS1, DGS3, DGS10，每个包含 id, name, fred_series_id, category, color
   - 验收：文件存在且 YAML 格式正确

6. [x] 在 `config/settings.py` 中添加 `load_series_config()` 函数，解析 series_config.yaml 返回系列列表
   - 验收：`python -c "from config.settings import load_series_config; print(load_series_config())"` 输出 6 个系列配置

### Phase 2: 存储仓库层

7. [x] 创建 `src/repositories/base.py`，定义 `SeriesRepository` 抽象基类，包含抽象方法：`read(series_id, start_date, end_date)`, `write(series_id, data, mode)`, `exists(series_id)`, `get_date_range(series_id)`
   - 验收：文件存在，类继承 ABC

8. [x] 创建 `src/repositories/base.py` 中的 `MetadataRepository` 抽象基类，包含抽象方法：`get(series_id)`, `update(series_id, updates)`, `get_all()`
   - 验收：文件存在，类继承 ABC

9. [x] 创建 `src/repositories/csv_repository.py`，实现 `CSVSeriesRepository` 类：
   - `read()`: 从 `data/raw/{series_id}.csv` 读取数据，支持日期范围过滤
   - `write()`: 写入 CSV，支持 replace/append 模式
   - `exists()`: 检查文件是否存在
   - `get_date_range()`: 返回数据的起止日期
   - 验收：`python -m pytest tests/test_csv_repository.py -v` 通过

10. [x] 创建 `src/repositories/csv_repository.py` 中的 `JSONMetadataRepository` 类，操作 `data/metadata.json` 文件
    - 验收：能读写 metadata.json

11. [x] 创建 `tests/test_csv_repository.py`，测试 CSVSeriesRepository 的 write→read 往返、append 模式、get_date_range
    - 验收：测试文件存在且可运行

### Phase 3: FRED 适配器

12. [x] 创建 `src/adapters/base.py`，定义 `DataSourceAdapter` 抽象基类，包含抽象方法：`fetch(series_id, start_date, end_date)`, `get_metadata(series_id)`
    - 验收：文件存在，类继承 ABC

13. [ ] 创建 `src/adapters/fred_adapter.py`，实现 `FREDAdapter` 类：
    - 使用 `config.settings.get_api_key()` 获取 API Key
    - `fetch()`: 调用 FRED API，返回 DataFrame(columns=['date','value'])
    - 处理缺失值 "." 转为跳过该行
    - 处理 value 字符串转 float
    - 验收：`python -c "from src.adapters.fred_adapter import FREDAdapter; print(FREDAdapter().fetch('SP500','2025-01-01','2025-01-10'))"` 输出 DataFrame
    - 注：代码已创建，等待 FRED_API_KEY 验证

### Phase 4: 数据服务层

14. [x] 创建 `src/services/data_service.py`，实现 `DataService` 类，构造函数接收 `SeriesRepository` 和 `MetadataRepository`
    - 验收：类存在，使用依赖注入

15. [x] 实现 `DataService.get_series(series_ids, start_date, end_date)` 方法：检查本地是否存在数据，存在则读取 CSV，不存在则调用适配器拉取并保存
    - 验收：首次调用创建 CSV，再次调用直接读取本地

16. [x] 实现 `DataService.refresh_data(series_ids, mode)` 方法：
    - mode=FULL: 全量拉取覆盖
    - mode=INCREMENTAL: 从 metadata.data_end_date + 1 天开始拉取，追加到 CSV
    - 验收：增量模式只拉取新数据

17. [x] 实现元数据自动更新：每次 refresh_data 后更新 metadata.json 的 `last_updated` 和 `data_end_date` 字段
    - 验收：查看 metadata.json 字段已更新

### Phase 5: 数据转换服务

18. [x] 创建 `src/services/transform.py`，实现 `normalize_to_scale(series, base_value)` 函数：将序列归一化为以 base_value 为 100 的比例
    - 验收：输入 [100, 110, 90] base=100，输出 [100.0, 110.0, 90.0]

19. [x] 实现 `filter_by_range(df, range_key)` 函数：根据 range_key (6m/1y/3y/5y/all) 过滤 DataFrame 的日期范围
    - 验收：filter_by_range(df, "6m") 返回最近约 180 天数据

20. [x] 创建 `tests/test_transform.py`，测试 normalize_to_scale 和 filter_by_range
    - 验收：`python -m pytest tests/test_transform.py -v` 通过

### Phase 6: Dash 应用

21. [x] 创建 `app.py`，初始化 Dash 应用，配置基本布局框架（控制面板区 + 图表区 + 状态栏）
    - 验收：`python app.py` 启动后浏览器访问 http://127.0.0.1:8050 显示页面
    - 注：需要 FRED_API_KEY 才能加载数据

22. [x] 创建 `src/components/controls.py`，实现控制面板组件：
    - 时间范围按钮组：6个月/1年/3年/5年/全部
    - 显示模式单选：绝对值/Scale
    - 数据系列多选框：从 series_config 读取生成
    - 验收：页面显示所有控件

23. [x] 创建 `src/components/chart.py`，实现图表组件：
    - 使用 Plotly Graph 显示多条折线
    - 支持 Hover 显示日期和数值
    - 支持 Zoom/Pan 交互
    - 验收：图表正常渲染，交互有效

24. [x] 在 `app.py` 中实现回调：时间范围按钮点击 → 更新图表数据范围
    - 验收：点击不同按钮，图表 X 轴范围变化

25. [x] 在 `app.py` 中实现回调：显示模式切换 → 重新计算 Y 轴数据（绝对值/归一化）
    - 验收：切换 Scale 模式后，所有线条起点对齐 100

26. [x] 在 `app.py` 中实现回调：数据系列勾选变化 → 更新图表显示的线条
    - 验收：勾选/取消系列，图表线条增减

27. [x] 在 `app.py` 中添加"更新数据"按钮和状态显示，点击触发 `DataService.refresh_data()`，显示更新结果
    - 验收：点击按钮后显示"已更新 X 条记录"

### Phase 7: 集成验证

28. [ ] 首次启动完整流程验证：删除 `data/raw/*.csv` 和 `data/metadata.json`，运行 `python app.py`，确认自动拉取 6 个系列并显示图表
    - 验收：6 个 CSV 文件生成，图表显示 6 条线

29. [ ] 增量更新验证：点击更新按钮，确认只拉取新数据追加
    - 验收：metadata.json 的 data_end_date 更新为今天

---

## Ralph Instructions

1. Work on the next incomplete criterion (marked [ ])
2. Check off completed criteria (change [ ] to [x])
3. Run tests after changes
4. Commit your changes frequently
5. When ALL criteria are [x], output: `<ralph>COMPLETE</ralph>`
6. If stuck on the same issue 3+ times, output: `<ralph>GUTTER</ralph>`
