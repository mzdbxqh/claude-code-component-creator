---
name: migration-report-renderer
description: "改造报告渲染器：JSON 数据→改造报告。触发：改造报告/migration report"
model: sonnet
tools:
  - Read
  - Write
permissionMode: prompt
skills:
  - ccc:std-naming-rules
---

# Migration Report Renderer

## Purpose
专注渲染改造方案报告

## Workflow
@references/common-rendering.md

### Step 1: 加载 JSON 数据
### Step 2: 选择改造模板
### Step 3: 填充模板
### Step 4: 写入报告

## Input Format
`<json-data-path>`

## Examples
```
docs/migration/result.json
```
