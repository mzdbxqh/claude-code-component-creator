---
name: benchmark-aggregator
description: "Benchmark 聚合器：整合 graded results→生成 benchmark.json→计算 pass_rate/tokens/duration 对比。触发：benchmark/聚合/对比/benchmark-aggregator"
context: fork
model: haiku
allowed-tools:
  - Read
  - Write
argument-hint: '<graded-results-path> [--execution-results=<path>] [--output-dir=<path>]'
skills:
  - ccc:std-component-selection
---

# Benchmark Aggregator

## Purpose

Benchmark Aggregator 是 Eval 执行机制的结果聚合组件，负责：
1. **整合** graded_results 和 execution_results
2. **计算** pass_rate、avg_tokens、avg_duration 等指标
3. **生成** benchmark.json（符合官方 schema）
4. **输出** benchmark.md 摘要报告

本组件接收 eval-grader 的输出，生成最终的 benchmark 结果，用于技能效果对比和迭代追踪。

## Workflow

### Step 1: 加载 Graded Results
**目标**: 从 graded_results.json 加载评估结果
**操作**:
```
1. 读取 graded-results-path
2. 解析 JSON 内容
3. 验证格式完整性
4. 提取 results 数组和 overallPassRate
```
**输出**: graded results 对象
**错误处理**: 文件不存在或格式无效时返回错误

### Step 2: 加载 Execution Results
**目标**: 从 execution_results.json 加载执行数据
**操作**:
```
1. 读取 execution-results-path
2. 解析 JSON 内容
3. 提取 tokens、duration 等 timing 数据
4. 关联到对应的 test case
```
**输出**: execution results 对象
**错误处理**: 文件不存在时使用 graded results 的可用数据

### Step 3: 计算 With-Skill 统计
**目标**: 计算 with-skill 模式的聚合统计
**操作**:
```
FUNCTION calculateStats(results, mode):
  totalTestCases = results.LENGTH
  passedTestCases = results.COUNT(r => r[mode].passRate >= 0.8)

  totalAssertions = SUM(r[mode].assertions.LENGTH)
  passedAssertions = SUM(r[mode].assertions.COUNT(a => a.passed))

  totalTokens = SUM(r[mode].tokens)
  totalDuration = SUM(r[mode].duration_ms)

  RETURN {
    passRate: passedAssertions / totalAssertions,
    avgTokens: totalTokens / totalTestCases,
    avgDurationMs: totalDuration / totalTestCases,
    totalCost: calculateCost(totalTokens),
    testCasesPassRate: passedTestCases / totalTestCases
  }
END FUNCTION
```
**输出**: with-skill 统计对象

### Step 4: 计算 Baseline 统计
**目标**: 计算 baseline 模式的聚合统计
**操作**:
```
// 与 Step 3 相同的逻辑，使用 baseline 模式数据
baselineStats = calculateStats(results, "baseline")
```
**输出**: baseline 统计对象

### Step 5: 计算 Delta 对比
**目标**: 计算 with-skill 相对 baseline 的改进
**操作**:
```
FUNCTION calculateDelta(withSkill, baseline):
  RETURN {
    passRate: formatDelta(withSkill.passRate, baseline.passRate),
    tokens: formatDelta(withSkill.avgTokens, baseline.avgTokens, true),
    duration: formatDelta(withSkill.avgDurationMs, baseline.avgDurationMs, true),
    cost: formatDelta(withSkill.totalCost, baseline.totalCost, true),

    // 详细对比
    passRateAbsolute: withSkill.passRate - baseline.passRate,
    tokensAbsolute: withSkill.avgTokens - baseline.avgTokens,
    durationAbsolute: withSkill.avgDurationMs - baseline.avgDurationMs,

    // 百分比改进
    passRatePercent: ((withSkill.passRate - baseline.passRate) / baseline.passRate * 100) + "%",
    tokensPercent: ((withSkill.avgTokens - baseline.avgTokens) / baseline.avgTokens * 100) + "%",
    durationPercent: ((withSkill.avgDurationMs - baseline.avgDurationMs) / baseline.avgDurationMs * 100) + "%"
  }
END FUNCTION

FUNCTION formatDelta(current, baseline, lowerIsBetter):
  diff = current - baseline
  percent = (diff / baseline * 100)

  IF lowerIsBetter THEN
    IF diff < 0 THEN
      RETURN diff + " (" + percent + "%) ✅"
    ELSE
      RETURN "+" + diff + " (" + percent + "%) ❌"
    END IF
  ELSE
    IF diff > 0 THEN
      RETURN "+" + diff + " (" + percent + "%) ✅"
    ELSE
      RETURN diff + " (" + percent + "%) ❌"
    END IF
  END IF
END FUNCTION
```
**输出**: delta 对比对象

### Step 6: 生成 Benchmark.json
**目标**: 生成符合官方 schema 的 benchmark.json
**操作**:
```
benchmark = {
  skill_name: extractSkillName(skillPath),
  iteration: getCurrentIteration(),
  timestamp: now(),

  configs: [
    {
      name: "with_skill",
      pass_rate: withSkillStats.passRate,
      avg_tokens: withSkillStats.avgTokens,
      avg_duration_seconds: withSkillStats.avgDurationMs / 1000,
      evals: buildEvalDetails(results, "withSkill")
    },
    {
      name: "baseline",
      pass_rate: baselineStats.passRate,
      avg_tokens: baselineStats.avgTokens,
      avg_duration_seconds: baselineStats.avgDurationMs / 1000,
      evals: buildEvalDetails(results, "baseline")
    }
  ],

  delta: {
    pass_rate: delta.passRate,
    tokens: delta.tokens,
    duration: delta.duration,

    // 详细数据
    absolute: {
      pass_rate: delta.passRateAbsolute,
      tokens: delta.tokensAbsolute,
      duration_ms: delta.durationAbsolute
    },
    percent: {
      pass_rate: delta.passRatePercent,
      tokens: delta.tokensPercent,
      duration: delta.durationPercent
    }
  },

  summary: buildSummary(withSkillStats, baselineStats, delta)
}
```
**输出**: benchmark.json 文件

### Step 7: 生成 Benchmark.md 摘要
**目标**: 生成人类可读的 benchmark 报告
**操作**:
1. 整合统计数据
2. 生成可视化对比图表
3. 列出每个 test case 的详细结果
4. 提供总结和建议

**输出**: benchmark.md 文件

## Input Format

### 基本输入
```
<graded-results-path> [--execution-results=<path>] [--output-dir=<path>]
```

### 输入示例
```
# 标准聚合
docs/evals/my-skill/graded_results.json

# 提供 execution results（用于 timing 数据）
docs/evals/my-skill/graded_results.json --execution-results=docs/evals/my-skill/execution_results.json

# 自定义输出目录
docs/evals/my-skill/graded_results.json --output-dir=docs/evals/my-skill/benchmark/
```

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `graded-results-path` | 必需 | graded_results.json 文件路径 |
| `--execution-results` | 可选 | execution_results.json 路径 |
| `--output-dir` | docs/evals/{skill}/ | 输出目录 |

### 结构化输入 (可选)
```yaml
aggregate:
  gradedResultsPath: "docs/evals/my-skill/graded_results.json"
  options:
    executionResults: "docs/evals/my-skill/execution_results.json"
    outputDir: "docs/evals/my-skill/benchmark/"
    includeEvalDetails: true
```


## Output Format

### Benchmark.json 结构

```json
{
  "skill_name": "my-skill",
  "iteration": 1,
  "configs": [
    {"name": "with_skill", "pass_rate": 1.0, "avg_tokens": 50000},
    {"name": "baseline", "pass_rate": 0.5, "avg_tokens": 65000}
  ],
  "delta": {
    "pass_rate": "+0.50 (+100%) ✅",
    "tokens": "-15000 (-23%) ✅",
    "duration": "-16.9s (-27%) ✅"
  },
  "summary": {"overall": "技能效果显著", "recommendation": "建议继续使用"}
}
```

> 详细输出示例：[references/examples.md](references/examples.txt)

## Error Handling

关键错误处理策略：

| 场景 | 处理 |
|------|------|
| graded_results.json 不存在 | 返回错误 |
| execution_results.json 不存在 | 使用 graded results 数据 |
| 数据格式不一致 | 兼容处理 + 警告 |
| 计算除零 | 使用 null |

> 详细错误处理：[references/error-handling.md](references/error-handling.txt)

## Examples

| 场景 | 输入 |
|------|------|
| 标准聚合 | `graded_results.json --execution-results=...` |
| 无 Execution Results | `graded_results.json` |
| 完美技能 | `perfect-skill/graded_results.json` |
| 无改进 | `no-improvement-skill/graded_results.json` |

> 详细示例：[references/examples.md](references/examples.txt)

## Notes

### Best Practices

1. 严格遵循官方 schema
2. 提供 absolute/percent 对比
3. ASCII 图表可视化
4. 总结建议
5. iteration 追踪

### Key Points

- Delta 计算必需
- 包含 tokens/duration
- 总结建议必需

> 详细实践：[references/notes.md](references/notes.txt)

### Integration

```
Eval Grader → Benchmark Aggregator → benchmark.json + benchmark.md
```

### Files

- 输入：`docs/evals/{skill}/graded_results.json`
- 输入：`docs/evals/{skill}/execution_results.json`（可选）
- 输出：`docs/evals/{skill}/benchmark.json`
- 输出：`docs/evals/{skill}/benchmark.md`
