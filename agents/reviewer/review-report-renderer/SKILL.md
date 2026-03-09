---
name: review-report-renderer
description: "审阅报告渲染器：JSON 审查数据→审阅报告。触发：审阅报告/review report/渲染审阅"
context: fork
argument-hint: '<json-data-path>'
model: sonnet
allowed-tools:
  - Read
  - Write
---

# Review Report Renderer

## Purpose
专注渲染审阅聚合报告，将 JSON 审查数据转换为格式化的 Markdown 报告。

## Workflow

@references/common-rendering.md

### Step 1: 加载审阅 JSON 数据
读取并验证审阅聚合 JSON 文件

### Step 2: 选择审阅报告模板
使用 review-aggregated 模板

### Step 3: 填充模板
将数据填充到模板占位符

### Step 4: 写入报告
保存为 Markdown 文件

## Input Format
```
<json-data-path>
```

## Output Format
生成的审阅报告 Markdown 文件

## Examples

### Example 1: 基本用法
```
docs/reviews/aggregated-result.json
```

## Error Handling
参考 @references/common-rendering.md
