---
name: dependency-report-renderer
description: "依赖报告渲染器：JSON 数据→依赖报告。触发：依赖报告/dependency report"
context: fork
argument-hint: '<json-data-path>'
model: sonnet
allowed-tools:
  - Read
  - Write
skills:
  - ccc:std-naming-rules
---

# Dependency Report Renderer

## Purpose
专注渲染依赖分析报告

## Workflow
@references/common-rendering.md

### Step 1: 加载 JSON 数据
### Step 2: 选择依赖模板
### Step 3: 填充模板
### Step 4: 写入报告

## Input Format
`<json-data-path>`

## Examples
```
docs/dependency/result.json
```
