# Generate RALPH_TASK.md from Design Document

根据设计文档生成符合 Ralph Wiggum 规范的任务文件。

## 使用方法

执行此命令时，请提供设计文档的路径，例如：
- `@MVP_DESIGN.md`
- `@design/mvp/design.md`

---

## Instructions

你是一个 Ralph Wiggum 任务生成助手。请按以下步骤执行：

### 第一步：理解 Ralph Wiggum 工作原理

阅读以下文件了解 Ralph Wiggum 的核心机制：

1. **@.cursor/ralph-scripts/ralph-common.sh** - 核心循环逻辑
2. **@.ralph/guardrails.md** - 教训记录格式
3. **@.ralph/progress.md** - 进度跟踪格式
4. **@RALPH_TASK_TEMPLATE.md** - 任务模板格式

Ralph 的核心理念：
- 状态保存在 git 和文件中，而非 LLM 上下文
- 用 `[ ]` 和 `[x]` checkbox 追踪任务完成状态
- 每次迭代从 `RALPH_TASK.md` 读取任务，从 `.ralph/` 读取上下文
- 当 context 接近上限时自动轮换到新的 agent

### 第二步：分析设计文档

阅读用户指定的设计文档（如 `$ARGUMENTS`），提取：

1. **项目名称和描述**
2. **技术栈要求**
3. **功能模块划分**
4. **具体实现任务**

### 第三步：生成 RALPH_TASK.md

按照 `@RALPH_TASK_TEMPLATE.md` 的格式，生成任务文件：

```markdown
---
task: [项目简短描述]
test_command: "[测试命令]"
---

# Task: [项目名称]

[一句话描述项目目标]

## Requirements

1. [技术栈要求 1]
2. [技术栈要求 2]
...

## Success Criteria

### Phase N: [阶段名称]
1. [ ] [具体可验证的任务]
2. [ ] [具体可验证的任务]
...

---

## Ralph Instructions

1. Work on the next incomplete criterion (marked [ ])
2. Check off completed criteria (change [ ] to [x])
3. Run tests after changes
4. Commit your changes frequently
5. When ALL criteria are [x], output: `<ralph>COMPLETE</ralph>`
6. If stuck on the same issue 3+ times, output: `<ralph>GUTTER</ralph>`
```

### 任务编写原则

1. **可验证性**：每个 `[ ]` 任务必须明确可验证（创建了什么文件、实现了什么功能）
2. **原子性**：每个任务应该在一次迭代内可完成
3. **顺序性**：按依赖关系排序，前置任务在前
4. **分阶段**：按功能模块或开发阶段分组

### 第四步：输出结果

直接编辑 `RALPH_TASK.md` 文件，将生成的内容写入。

---

## 输入

设计文档路径：$ARGUMENTS
