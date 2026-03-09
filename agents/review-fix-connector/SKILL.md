---
name: review-fix-connector
description: "Review→Fix 连接器：解析 Review 报告，生成 Fix 输入，触发修复流程"
model: sonnet
context: fork
allowed-tools:
  - Read
  - Write
  - Task
---

# Review-Fix Connector

## Purpose

解析 Review 报告，提取问题和修复建议，生成 Fix 子代理的输入，触发修复流程。

## Workflow

### Step 1: 解析 Review 报告
**目标**: 读取 Review 报告
**操作**:
1. 读取 review-report.md
2. 解析问题列表
**输出**: 问题列表

### Step 2: 生成 Fix 输入
**目标**: 构建 Fix 子代理输入
**操作**:
1. 将问题转换为 Fix 任务
2. 添加优先级标注
**输出**: Fix 任务列表

### Step 3: 触发 Fix 流程
**目标**: 执行 Fix 子代理
**操作**:
1. 使用 Task 工具调用 fix-orchestrator
2. 传递 Fix 任务列表
**输出**: Fix 执行结果

## Input Format

```
[review-report-path]
```

## Output Format

```json
{
  "status": "success|error",
  "fix_tasks": [
    {
      "id": "FIX-001",
      "priority": "P0",
      "issue_id": "SKILL-001",
      "description": "修复 name 格式错误",
      "location": "skills/xxx/SKILL.md"
    }
  ],
  "fix_result": {
    "status": "completed",
    "fixed_count": 3,
    "report_path": "docs/fixes/fix-report.md"
  }
}
```

## Error Handling

| 错误场景 | 处理策略 | 示例 |
|----------|----------|------|
| Review 报告不存在 | 返回错误 | "Review 报告不存在" |
| 无法解析问题 | 跳过并继续 | "跳过无法解析的问题" |
| Fix 执行失败 | 返回错误 | "Fix 执行失败：XXX" |

## Examples

### Example 1: 成功触发 Fix

**输入**:
```
docs/reviews/2026-03-08-review-report.md
```

**输出**:
```json
{
  "status": "success",
  "fix_tasks": [
    {"id": "FIX-001", "priority": "P0", "issue_id": "SKILL-001", "description": "修复 name 格式错误"}
  ],
  "fix_result": {"status": "completed", "fixed_count": 1}
}
```
