---
task: 处理新闻元数据，生成中文摘要和市场分析
test_command: "ls -la news/data/"
---

# Task: 新闻处理 (2026-01-24 至 2026-01-25)

处理指定日期范围的新闻元数据，获取新闻内容，生成中文摘要和市场影响分析，按日期保存结果。

## Requirements

1. 输入: `news/meta_data/macro_economy/{date}.json` 元数据文件
2. 输出: `news/data/{date}.json` 处理结果文件
3. 日期范围: 2026-01-24 至 2026-01-25
4. 摘要限制: < 100 中文字符
5. 分析限制: < 50 中文字符

## Success Criteria

### Phase 1: 准备工作
1. [x] 确认输出目录 `news/data/` 存在，不存在则创建

### Phase 2: 处理 2026-01-24
1. [x] 读取 `news/meta_data/macro_economy/2026-01-24.json`，获取 articles 列表
2. [ ] 逐条处理文章：获取内容、判断分类(宏观经济/国家政策/地缘政治)、生成摘要(<100字)、生成分析(<50字)
3. [ ] 保存结果到 `news/data/2026-01-24.json`，格式符合规范

### Phase 3: 处理 2026-01-25
1. [ ] 读取 `news/meta_data/macro_economy/2026-01-25.json`，获取 articles 列表
2. [ ] 逐条处理文章：获取内容、判断分类、生成摘要(<100字)、生成分析(<50字)
3. [ ] 保存结果到 `news/data/2026-01-25.json`，格式符合规范

### Phase 4: 生成报告
1. [ ] 输出处理统计：总天数、总文章数、各类别数量、失败列表(如有)

---

## 输出文件格式

每个 `news/data/{date}.json` 文件格式：

```json
{
  "date": "YYYY-MM-DD",
  "processed_time": "ISO时间戳",
  "article_count": 处理成功的文章数量,
  "articles": [
    {
      "url": "原始url",
      "title": "原始标题",
      "category": "宏观经济|国家政策|地缘政治",
      "summary": "中文摘要，<100字",
      "analysis": "中文市场影响分析，<50字"
    }
  ]
}
```

## 分类规则

- **宏观经济**: GDP、通胀、利率、就业、贸易数据等经济指标
- **国家政策**: 财政政策、货币政策、监管法规、税收政策等
- **地缘政治**: 国际关系、战争冲突、制裁、政治事件等
- 不确定时默认归类为"宏观经济"

## 分析维度

分析需考虑对以下市场的影响：
- 美国股市 (利好/利空/中性)
- 债券价格
- 其他金融产品 (黄金、原油、美元等)

格式示例: "利好科技股，美债收益率或上行，美元走强"

---

## Secrets

| 用途 | 文件路径 |
|------|----------|
| FRED API Key | `secrets/FRED_API_KEY` |

**不要硬编码任何密钥，始终从 `secrets/` 目录的文件读取。**

---

## Ralph Instructions

1. Work on the next incomplete criterion (marked [ ])
2. Check off completed criteria (change [ ] to [x])
3. Run tests after changes
4. Commit your changes frequently
5. When ALL criteria are [x], output: `<ralph>COMPLETE</ralph>`
6. If stuck on the same issue 3+ times, output: `<ralph>GUTTER</ralph>`
