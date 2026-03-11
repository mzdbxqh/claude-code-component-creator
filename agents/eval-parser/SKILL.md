---
name: eval-parser
description: "Eval 解析器：解析 evals/evals.json 文件，验证格式，提取测试用例"
model: haiku
tools:
  - Read
  - Grep
  - Glob
permissionMode: prompt
skills:
  - ccc:std-evidence-chain
  - ccc:std-component-selection
---

# Eval Parser

## Purpose

解析 evals/evals.json 文件，验证 JSON 格式，提取测试用例供执行器使用。

## Workflow

### Step 1: 定位 evals.json
**目标**: 找到 evals/evals.json 文件
**操作**:
1. 检查目标目录是否存在 evals/evals.json
2. 验证文件可读性
**输出**: 文件路径
**错误处理**: 文件不存在时返回 INFO 级别问题

### Step 2: 解析 JSON
**目标**: 解析 evals.json 内容
**操作**:
1. 读取文件内容
2. 验证 JSON 格式
3. 提取 testCases 数组
**输出**: 解析后的测试用例列表
**错误处理**: JSON 格式错误时返回 ERROR

### Step 3: 验证 Schema
**目标**: 验证测试用例结构
**操作**:
1. 检查必需字段 (id, name, prompt)
2. 检查字段格式
**输出**: 验证通过的测试用例列表
**错误处理**: 字段缺失时返回 WARNING

## Input Format

```
[evals-path]
```

## Output Format

```json
{
  "status": "success|error",
  "evals_path": "evals/evals.json",
  "test_cases": [
    {"id": "TC-001", "name": "...", "prompt": "..."}
  ],
  "validation_errors": []
}
```

## Error Handling

| 错误场景 | 处理策略 | 示例 |
|----------|----------|------|
| evals.json 不存在 | 返回 INFO 级别提示 | "evals.json 不存在，跳过 Eval 机制" |
| JSON 格式错误 | 返回 ERROR 并停止 | "JSON 解析失败：第 X 行" |
| 缺少必需字段 | 返回 WARNING 并继续 | "TC-001 缺少 prompt 字段" |
| testCases 为空 | 返回 INFO 并继续 | "evals.json 为空，无测试用例" |

## Examples

### Example 1: 成功解析

**输入**:
```
evals/evals.json
```

**输出**:
```json
{
  "status": "success",
  "evals_path": "evals/evals.json",
  "test_cases": [
    {"id": "TC-001", "name": "简单技能创建", "prompt": "创建一个 TODO 技能"},
    {"id": "TC-002", "name": "复杂 SubAgent 创建", "prompt": "创建代码审查器"}
  ],
  "validation_errors": []
}
```

### Example 2: 文件不存在

**输入**:
```
evals/evals.json
```

**输出**:
```json
{
  "status": "info",
  "evals_path": "evals/evals.json",
  "test_cases": [],
  "validation_errors": ["文件不存在"]
}
```

### Example 3: JSON 格式错误

**输入**:
```
evals/evals.json
```

**输出**:
```json
{
  "status": "error",
  "evals_path": "evals/evals.json",
  "test_cases": [],
  "validation_errors": ["JSON 解析失败：第 15 行缺少逗号"]
}
```
