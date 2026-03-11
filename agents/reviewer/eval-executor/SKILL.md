---
name: eval-executor
description: "Eval 执行器：并行执行测试用例→捕获 timing 数据→区分 with-skill/baseline 模式。触发：eval/执行/测试/eval-executor"
model: sonnet
tools:
  - Read
  - Write
  - Task
  - Glob
permissionMode: prompt
skills:
  - ccc:std-evidence-chain
  - ccc:std-component-selection
---

# Eval Executor

## Purpose

Eval Executor 是 Eval 执行机制的核心组件，负责：
1. **并行执行** 测试用例（使用 Agent 系统）
2. **支持模式** with-skill、baseline、both
3. **捕获** timing 数据（tokens、duration_ms）
4. **输出** 结构化的执行结果

本组件接收 eval-parser 的输出，执行实际测试并生成 execution_results.json 供 eval-grader 使用。

## Workflow

### Step 1: 加载测试用例
**目标**: 从 evals.json 加载测试用例
**操作**:
```
1. 读取 evals-json-path
2. 调用 ccc:eval-parser 验证格式（可选）
3. 提取 evals 数组
4. 准备执行队列
```
**输出**: 测试用例列表
**错误处理**: evals.json 无效时返回错误

### Step 2: 准备执行环境
**目标**: 根据模式准备执行环境
**操作**:

| 模式 | 说明 | 执行配置 |
|------|------|----------|
| with-skill | 加载技能上下文 | 读取 skill-path 的 SKILL.md，注入 context |
| baseline | 不加载技能 | 仅使用基础 prompt，无技能上下文 |
| both | 两种模式都执行 | with-skill + baseline 并行 |

**配置详情**:
```yaml
with_skill_config:
  - 读取 skill-path/SKILL.md
  - 提取 name, description, context, tools
  - 准备技能注入 prompt

baseline_config:
  - 不读取任何技能文件
  - 仅使用用户 prompt
```

**输出**: 执行配置对象
**错误处理**: skill-path 无效时降级为 baseline

### Step 3: 并行执行测试
**目标**: 使用 Agent 系统并行执行所有测试用例
**操作**:
```
FUNCTION executeTests(testCases, mode):
  results = []

  FOR each testCase IN testCases DO
    IF mode == "both" THEN
      // 创建两个 Task：with-skill 和 baseline
      taskWithSkill = CREATE Task {
        name: "eval-test-" + testCase.id + "-with-skill",
        prompt: buildPrompt(testCase.prompt, skillContext),
        model: "sonnet"
      }

      taskBaseline = CREATE Task {
        name: "eval-test-" + testCase.id + "-baseline",
        prompt: testCase.prompt,
        model: "sonnet"
      }

      results.ADD({
        id: testCase.id,
        withSkill: { taskId: taskWithSkill.id, status: "pending" },
        baseline: { taskId: taskBaseline.id, status: "pending" }
      })

    ELSE IF mode == "with-skill" THEN
      task = CREATE Task {
        name: "eval-test-" + testCase.id,
        prompt: buildPrompt(testCase.prompt, skillContext),
        model: "sonnet"
      }
      results.ADD({ id: testCase.id, taskId: task.id, status: "pending" })

    ELSE IF mode == "baseline" THEN
      task = CREATE Task {
        name: "eval-test-" + testCase.id + "-baseline",
        prompt: testCase.prompt,
        model: "sonnet"
      }
      results.ADD({ id: testCase.id, taskId: task.id, status: "pending" })
    END IF
  END FOR

  // 等待所有 Task 完成
  WAIT FOR ALL tasks

  RETURN results
END FUNCTION
```
**输出**: Task 执行结果集合
**错误处理**: 单个 Task 失败不影响其他 Task

### Step 4: 捕获 Timing 数据
**目标**: 从 Task 元数据捕获 tokens 和 duration
**操作**:
```
FOR each result IN results DO
  // 从 Task 响应中提取元数据
  result.tokens = task.response.usage.total_tokens
  result.duration_ms = task.endTime - task.startTime
  result.output = task.response.content
  result.model = task.response.model
END FOR
```
**输出**: 包含 timing 数据的结果
**错误处理**: 元数据缺失时使用默认值或 null

### Step 5: 生成执行结果文件
**目标**: 输出结构化的 execution_results.json
**操作**:
1. 整合所有测试结果
2. 添加执行时间戳
3. 添加模式信息
4. 写入 output-dir

**输出文件**:
- `execution_results.json`: 完整结果
- `execution_summary.md`: 摘要报告

**输出结构**:
```json
{
  "executionId": "exec-2026-03-06-001",
  "timestamp": "2026-03-06T10:30:00Z",
  "mode": "both",
  "skillPath": "agents/my-skill/SKILL.md",
  "totalTestCases": 2,
  "completedTestCases": 2,
  "results": [
    {
      "id": 1,
      "evalName": "xlsx-profit-margin-calc",
      "prompt": "ok so my boss just sent me this xlsx file...",
      "withSkill": {
        "status": "completed",
        "output": "...",
        "tokens": 52000,
        "duration_ms": 48500,
        "model": "claude-sonnet-4-5-20250929"
      },
      "baseline": {
        "status": "completed",
        "output": "...",
        "tokens": 65000,
        "duration_ms": 62100,
        "model": "claude-sonnet-4-5-20250929"
      }
    }
  ],
  "aggregatedStats": {
    "withSkill": {
      "avgTokens": 52000,
      "avgDurationMs": 48500
    },
    "baseline": {
      "avgTokens": 65000,
      "avgDurationMs": 62100
    }
  }
}
```

## Input Format

### 基本输入
```
<evals-json-path> [--mode=with-skill|baseline|both] [--skill-path=<path>] [--output-dir=<path>]
```

### 输入示例
```
# 执行 with-skill 模式
agents/my-skill/evals/evals.json --mode=with-skill --skill-path=agents/my-skill/SKILL.md

# 执行 both 模式（默认）
agents/my-skill/evals/evals.json

# 自定义输出目录
agents/my-skill/evals/evals.json --output-dir=docs/evals/my-skill/
```

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `evals-json-path` | 必需 | evals/evals.json 文件路径 |
| `--mode` | both | 执行模式：with-skill、baseline、both |
| `--skill-path` | 推断 | 技能文件路径（with-skill 模式必需） |
| `--output-dir` | docs/evals/ | 输出目录 |

### 结构化输入 (可选)
```yaml
execute:
  evalsJsonPath: "agents/my-skill/evals/evals.json"
  options:
    mode: "both"
    skillPath: "agents/my-skill/SKILL.md"
    outputDir: "docs/evals/my-skill/"
    maxConcurrency: 4
    timeout: 300
```


## Output Format

### 标准输出结构

```json
{
  "executionId": "exec-2026-03-06-001",
  "mode": "both",
  "status": "COMPLETED",
  "results": [
    {"id": 1, "withSkill": {"status": "completed", "tokens": 52000}, "baseline": {"status": "completed", "tokens": 65000}}
  ],
  "aggregatedStats": {
    "withSkill": {"avgTokens": 52000, "avgDurationMs": 48500},
    "baseline": {"avgTokens": 65000, "avgDurationMs": 62100}
  },
  "comparison": {"tokenSavings": "-13000 (-20%)", "durationSavings": "-13.6s (-22%)"}
}
```

> 详细输出示例：[references/examples.md](references/examples.txt)

## Error Handling

关键错误处理策略：

| 场景 | 处理 |
|------|------|
| evals.json 无效 | 返回错误，建议先运行 ccc:eval-parser |
| Task 创建失败 | 记录错误，继续其他 |
| Task 超时 | 标记 timeout，继续其他 |
| skill-path 不存在 | 降级为 baseline |
| tokens 缺失 | 使用估算值 |

> 详细错误处理：[references/error-handling.md](references/error-handling.txt)

## Examples

| 场景 | 输入 |
|------|------|
| Both 模式 | `evals.json` |
| With-Skill | `evals.json --mode=with-skill` |
| Baseline | `evals.json --mode=baseline` |
| 超时处理 | `evals.json --timeout=60` |
| 部分失败 | `unstable-skill/evals/evals.json` |

> 详细示例：[references/examples.md](references/examples.txt)

## Notes

### Best Practices

1. 并行优先
2. 超时保护（默认 300 秒）
3. 详细日志
4. 容错处理
5. 数据完整

### Key Points

- 不可串行执行
- 不可忽略元数据
- 不可缺失 comparison

> 详细实践：[references/notes.md](references/notes.txt)

### Integration

```
Eval Parser → Eval Executor → Eval Grader → Benchmark Aggregator
```

### Files

- 输入：`{skill-path}/evals/evals.json`
- 输出：`docs/evals/{skill-name}/execution_results.json`
- 输出：`docs/evals/{skill-name}/execution_summary.md`
