---
name: ccc:cmd-review-migration-plan
model: sonnet
context: fork
disable-model-invocation: true
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, Task]
description: "审查Agent→Skill迁移计划质量。触发：迁移审查/方案评估。输出21个检测点的审查报告。"
argument-hint: "<file-path> [--format=json|markdown] [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:review-migration-plan

Reviews Agent→Skill migration plan quality - checks completeness, risk assessment, and best practice compliance.

## 模型要求

- **推荐**: Claude Sonnet 4.5+ (高效能,最佳性价比)
- **可用**: Claude Opus 4.5+ (最高质量,深度分析)
- **最小**: Claude Sonnet 4.5+ (最低要求)

### 功能需求
- 需要支持 Tool Use (Bash, Read, Write, Edit, Glob, Grep, Task)
- 需要支持多轮对话和并行检测
- 需要处理 21 个检测点的完整分析
- 建议上下文窗口 >= 200K tokens (处理完整迁移计划)

## SubAgents 协作

本工作流使用以下 SubAgents 进行任务分解和并行执行：

### 核心 Agents
- **ccc:migration-review-aggregator**: 迁移审查聚合器，协调 5 个批次的并行检测
- **ccc:migration-reviewer-core**: 迁移审查核心，执行单个批次的检测任务
- **ccc:migration-report-renderer**: 迁移报告渲染器，生成 JSON/Markdown 格式报告

### 调度策略
- **串行执行**: cmd-review-migration-plan → ccc:migration-review-aggregator → migration-report-renderer
- **并行执行**: 5 个批次的检测并行执行（文档结构、依赖分析、风险评估、最佳实践、工作量规划）
- **错误处理**: 单个批次失败不影响其他批次，继续执行并在报告中标记

### Agent 输入输出
| Agent | 输入 | 输出 |
|-------|------|------|
| ccc:migration-review-aggregator | 迁移计划文档路径 | 所有批次检测结果 |
| ccc:migration-reviewer-core | 单个批次检测任务 | 批次检测结果（JSON）|
| ccc:migration-report-renderer | 聚合检测结果 + format 参数 | JSON/Markdown 报告 |

### 调用示例
```
用户: /ccc:review-migration-plan agent-to-skill-detailed-plan.md
  ↓
cmd-review-migration-plan 读取迁移计划文档
  ↓
调用 migration-review-aggregator (协调并行检测):
  并行执行:
    - Batch 1: 文档结构检测 (5 个检测点)
    - Batch 2: 依赖分析检测 (4 个检测点)
    - Batch 3: 风险评估检测 (4 个检测点)
    - Batch 4: 最佳实践检测 (4 个检测点)
    - Batch 5: 工作量规划检测 (4 个检测点)
  ↓
调用 migration-report-renderer (生成报告)
  ↓
cmd-review-migration-plan 输出 JSON 报告
```

## 用法

```
/review-migration-plan <file-path> [--format=json|markdown] [--lang=zh-cn|en-us|ja-jp]
```

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |

## 参数

- `file-path` (必填): 改造方案文档路径
- `--format` (可选): 输出格式，默认为 `json`
  - `json`: 结构化 JSON 报告
  - `markdown`: 人类可读的 Markdown 报告

## 示例

```bash
# 审阅改造方案，输出 JSON
/review-migration-plan agent-to-skill-detailed-plan.md

# 审阅并生成 Markdown 报告
/review-migration-plan agent-to-skill-detailed-plan.md --format=markdown

# 使用英文输出审阅报告
/review-migration-plan agent-to-skill-detailed-plan.md --lang=en-us
```

## 工作流程

1. **启动聚合器**：调用 `ccc:migration-review-aggregator` Subagent
2. **并行检测**：聚合器并行启动 5 个 `ccc:migration-reviewer-core` 实例
3. **收集结果**：等待所有批次完成
4. **生成报告**：整合结果并输出

## 检测范围

| 批次 | 检查内容 | 检测项数 |
|------|----------|----------|
| batch-1-structure | 文档结构完整性 | 5 |
| batch-2-dependency | 依赖分析质量 | 4 |
| batch-3-risk | 风险评估完整性 | 4 |
| batch-4-practice | 最佳实践符合度 | 4 |
| batch-5-planning | 工作量与回滚策略 | 4 |

**总计**: 21 个检测点

## Output Specification

### Console Output

```
Migration Plan Review: agent-to-skill-detailed-plan.md

Total Batches: 5
Completed: 5/5
Issues Found: 8 (Errors: 3, Warnings: 4, Info: 1)

Status: COMPLETED with issues

Report saved to: docs/reviews/2026-03-02-plan-migration-review.md
```

### File Output

| Attribute | Value |
|-----------|-------|
| **Directory** | `docs/reviews/` |
| **Filename** | `YYYY-MM-DD-<filename>-migration-review.md` |
| **Format** | Markdown |
| **Overwrite** | No (timestamp ensures uniqueness) |

**Example:**
- `/review-migration-plan agent-to-skill-detailed-plan.md` → `docs/reviews/2026-03-02-agent-to-skill-detailed-plan-migration-review.md`

### Report Structure

| Section | Content |
|---------|---------|
| Overview | File reviewed, review date, batches completed |
| Summary | Total issues by severity |
| Issues by Category | Structure, Dependency, Risk, Practice, Planning |
| Severity Breakdown | Errors, Warnings, Info items |
| Recommendations | Prioritized fix suggestions |
| Details | Full issue list with line references |

### Output Formats

The command supports two output formats via `--format` parameter:

**JSON Format:** Structured data for programmatic processing
**Markdown Format:** Human-readable report (saved to file)

### File Access

```bash
# View the generated report
cat docs/reviews/YYYY-MM-DD-<filename>-migration-review.md

# List all migration review reports
ls -la docs/reviews/
```

## 严重级别说明

| 级别 | 含义 | 建议操作 |
|------|------|----------|
| error | 关键问题，必须修复 | 改造前必须解决 |
| warning | 潜在问题，影响质量 | 建议修复 |
| info | 改进建议 | 可选优化 |

## 常见检测项

### Error 级别
- MP001: 缺少概述章节
- MP003: 缺少风险评估
- MP006: 缺少工具依赖分析
- MP011: 缺少缓解措施
- MP018: 缺少工作量估算
- MP020: 缺少回滚策略

### Warning 级别
- MP005: 章节内容过短
- MP007: 缺少外部服务依赖
- MP012: 缺少优先级排序
- MP017: 缺少示例设计

## 故障排除

### 审阅失败

如果审阅失败，可能原因：
1. 文件路径不存在
2. 文件不是有效的 Markdown 格式
3. 超过 2 个检测批次失败

**解决方法**：检查文件路径和格式后重试。

## 架构流程

```
用户调用 /review-migration-plan
    ↓
调用 ccc:migration-review-aggregator
    ↓
并行启动 5 个 migration-reviewer-core
    ↓
┌─────────┬─────────┬─────────┬─────────┬─────────┐
│ batch-1 │ batch-2 │ batch-3 │ batch-4 │ batch-5 │
│ struct  │ depend  │ risk    │ practice│ plan    │
└────┬────┴────┬────┴────┬────┴────┬────┴────┬────┘
     └─────────┴────┬────┴─────────┘
                    ↓
              收集结果
                    ↓
              整合去重
                    ↓
              生成报告
```

## 相关组件

- **ccc:migration-review-aggregator**: 结果聚合器 (`reviewer/migration-review-aggregator/SKILL.md`)
- **ccc:migration-reviewer-core**: 检测核心 (`reviewer/migration-reviewer-core/SKILL.md`)
- **检测模式定义**: (`reviewer/knowledge/migration-patterns/batches/`)

## 使用示例 (Examples)

### Example 1: 快速审阅（JSON 格式）

```bash
/review-migration-plan agent-to-skill-detailed-plan.md
```

**输入**: Agent 到 Skill 改造方案文档

**输出**: JSON 格式审阅报告（控制台输出）
```json
{
  "file": "agent-to-skill-detailed-plan.md",
  "totalBatches": 5,
  "completed": 5,
  "issues": {
    "errors": 3,
    "warnings": 4,
    "info": 1
  },
  "details": [
    {"id": "MP001", "severity": "error", "message": "缺少概述章节"},
    {"id": "MP005", "severity": "warning", "message": "章节内容过短"}
  ]
}
```
- 报告同时保存至：`docs/reviews/2026-03-11-agent-to-skill-detailed-plan-migration-review.md`

### Example 2: 人类可读报告（Markdown 格式）

```bash
/review-migration-plan docs/plans/refactor-plan.md --format=markdown
```

**输入**: 重构计划文档，指定 Markdown 输出格式

**输出**: 人类可读的 Markdown 报告
```
Migration Plan Review: refactor-plan.md

总体状态: ⚠️ COMPLETED with issues

批次完成情况:
  ✓ batch-1-structure (5/5 检测点)
  ✓ batch-2-dependency (4/4 检测点)
  ⚠️ batch-3-risk (2/4 检测点) - 2 个问题
  ✓ batch-4-practice (4/4 检测点)
  ✓ batch-5-planning (4/4 检测点)

关键问题:
  [ERROR] MP003: 缺少风险评估章节
  [ERROR] MP011: 高风险项缺少缓解措施
  [WARNING] MP012: 缺少风险优先级排序

建议操作:
  1. 补充完整的风险评估章节
  2. 为每个高风险项添加具体缓解措施
  3. 按优先级排序风险列表

Report saved to: docs/reviews/2026-03-11-refactor-plan-migration-review.md
```

### Example 3: 英文审阅（国际化输出）

```bash
/review-migration-plan migration-proposal.md --format=markdown --lang=en-us
```

**输入**: 改造提案文档，英文输出

**输出**: 英文 Markdown 格式的审阅报告
```
Migration Plan Review: migration-proposal.md

Status: ✓ PASSED

Batch Results:
  ✓ batch-1-structure (5/5 checks passed)
  ✓ batch-2-dependency (4/4 checks passed)
  ✓ batch-3-risk (4/4 checks passed)
  ✓ batch-4-practice (4/4 checks passed)
  ✓ batch-5-planning (4/4 checks passed)

Total Issues: 0

Quality Grade: A (Excellent)

The migration plan meets all quality standards.
Ready for implementation.

Report saved to: docs/reviews/2026-03-11-migration-proposal-migration-review.md
```
