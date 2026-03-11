---
name: benchmark-aggregator
description: "Benchmark 聚合器：聚合所有测试结果，生成 benchmark.json 和 benchmark.md"
model: haiku
tools:
  - Read
  - Write
permissionMode: prompt
skills:
  - ccc:std-evidence-chain
  - ccc:std-component-selection
---

# Benchmark Aggregator

## Purpose

聚合所有测试结果，计算通过率、平均时间、token 使用，生成 benchmark.json 和 benchmark.md。

## Workflow

### Step 1: 收集评分结果
**目标**: 从 ccc:eval-grader 获取所有评分
**操作**:
1. 读取所有测试用例评分
2. 按配置分组 (with-skill, baseline)
**输出**: 评分结果集合

### Step 2: 计算统计信息
**目标**: 计算通过率、平均值
**操作**:
1. 计算每个配置的 pass_rate
2. 计算 avg_tokens
3. 计算 avg_duration_seconds
**输出**: 统计信息

### Step 3: 生成 benchmark.json
**目标**: 输出结构化 benchmark 数据
**操作**:
1. 构建 benchmark JSON 结构
2. 写入文件
**输出**: benchmark.json

### Step 4: 生成 benchmark.md
**目标**: 输出可读报告
**操作**:
1. 从 JSON 生成 Markdown 报告
2. 包含对比表格和 delta 分析
**输出**: benchmark.md

## Input Format

```json
{
  "grades": [
    {
      "test_case_id": "TC-001",
      "with_skill": {"passed": true, "score": 95, "duration_ms": 1234, "tokens_used": 567},
      "baseline": {"passed": true, "score": 90, "duration_ms": 2345, "tokens_used": 678}
    }
  ]
}
```

## Output Format

### benchmark.json

```json
{
  "timestamp": "2026-03-08T19:00:00Z",
  "summary": {
    "total_tests": 8,
    "with_skill": {
      "pass_rate": 100,
      "avg_duration_seconds": 45.5,
      "avg_tokens": 1234
    },
    "baseline": {
      "pass_rate": 87.5,
      "avg_duration_seconds": 67.8,
      "avg_tokens": 2345
    },
    "delta": {
      "time_improvement": "-33%",
      "token_improvement": "-47%",
      "pass_rate_improvement": "+12.5%"
    }
  },
  "test_results": [...]
}
```

### benchmark.md

```markdown
# Eval Benchmark 报告

**生成时间**: 2026-03-08 19:00:00

## 汇总

| 配置 | 通过率 | 平均时间 | 平均 Token |
|------|--------|----------|------------|
| with-skill | 100% | 45.5s | 1,234 |
| baseline | 87.5% | 67.8s | 2,345 |
| **改进** | **+12.5%** | **-33%** | **-47%** |

## 详细结果

| 测试用例 | with-skill | baseline | 改进 |
|----------|------------|----------|------|
| TC-001 | ✅ 95 (45s) | ✅ 90 (67s) | 时间 -33% |
| TC-002 | ✅ 92 (50s) | ❌ FAIL | 通过率 +12.5% |
```

## Error Handling

| 错误场景 | 处理策略 | 示例 |
|----------|----------|------|
| 评分结果缺失 | 使用空结果 | "无评分结果，生成空报告" |
| 计算异常 | 使用默认值 | "计算失败，使用默认统计" |
| 文件写入失败 | 重试 1 次 | "写入失败，重试中" |

## Examples

### Example 1: 完整报告

**输入**:
```json
{
  "grades": [
    {
      "test_case_id": "TC-001",
      "with_skill": {"passed": true, "score": 95, "duration_ms": 1234, "tokens_used": 567},
      "baseline": {"passed": true, "score": 90, "duration_ms": 2345, "tokens_used": 678}
    }
  ]
}
```

**输出**: benchmark.json 和 benchmark.md 文件已生成
