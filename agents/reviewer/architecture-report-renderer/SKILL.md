---
name: architecture-report-renderer
description: "架构报告渲染器：JSON 数据→架构报告。触发：架构报告/architecture report"
context: fork
argument-hint: '<json-data-path>'
model: sonnet
allowed-tools:
  - Read
  - Write
---

# Architecture Report Renderer

## Purpose
专注渲染架构分析报告

## Workflow
@references/common-rendering.md

### Step 1: 加载 JSON 数据
### Step 2: 选择架构模板
### Step 3: 填充模板
### Step 4: 写入报告

## Input Format
`<json-data-path>`

## Examples
```
docs/architecture/result.json
```
