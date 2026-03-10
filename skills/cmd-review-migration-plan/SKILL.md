---
name: ccc:review-migration-plan
description: 改造方案审阅模式 - 检查 Agent → Skill 改造方案质量
argument-hint: "<file-path> [--format=json|markdown] [--lang=zh-cn|en-us|ja-jp]"
---

# /review-migration-plan

对 Agent → Skill 改造方案进行质量审阅，检测方案完整性、风险评估、最佳实践符合度等问题。

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

1. **启动聚合器**：调用 `migration-review-aggregator` Subagent
2. **并行检测**：聚合器并行启动 5 个 `migration-reviewer-core` 实例
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
调用 migration-review-aggregator
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

- **migration-review-aggregator**: 结果聚合器 (`reviewer/migration-review-aggregator/SKILL.md`)
- **migration-reviewer-core**: 检测核心 (`reviewer/migration-reviewer-core/SKILL.md`)
- **检测模式定义**: (`reviewer/knowledge/migration-patterns/batches/`)
