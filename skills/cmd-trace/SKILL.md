---
name: ccc:cmd-trace
model: sonnet
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
description: "Generates comprehensive traceability matrix linking intent requirements to blueprint elements and delivery implementations with coverage analysis"
argument-hint: "<project-id> [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:trace

Generates full traceability matrix for the project.

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |

## Output Specification

### Console Output

```
Traceability Matrix: my-project

Intent Requirement          │ Blueprint Element      │ Delivery File:Line
────────────────────────────┼────────────────────────┼───────────────────
Auto-deploy                 │ deployment-workflow    │ deploy-skill.md:45
K8s support                 │ k8s-config             │ deploy-skill.md:67
Error handling              │ rollback-strategy      │ deploy-skill.md:89
GitOps workflow             │ git-trigger            │ deploy-skill.md:120

Coverage: 95% (19/20 requirements traced)
```

### File Output

| Attribute | Value |
|-----------|-------|
| **Directory** | `docs/traces/` |
| **Filename** | `YYYY-MM-DD-<project-id>-trace.md` |
| **Format** | Markdown |
| **Overwrite** | No (timestamp ensures uniqueness) |

**Example:**
- `/ccc:trace my-project` → `docs/traces/2026-03-02-my-project-trace.md`

### Report Structure

| Section | Content |
|---------|---------|
| Overview | Project traced, trace date |
| Traceability Matrix | Intent → Blueprint → Delivery mapping |
| Coverage Analysis | Percentage and gaps |
| Requirements | List of traced requirements |
| Gaps | Untraced or partially traced items |
| Summary | Overall coverage status |

## Workflow

### Step 1: Validate Project
**目标**: 验证项目存在性
**操作**: 检查项目 ID 是否有效
**输出**: 验证结果
**错误处理**: 项目不存在时使用 /ccc:projects 列出可用项目；项目 ID 格式无效时显示正确格式示例

### Step 2: Collect Traceable Artifacts
**目标**: 收集可追溯制品
**操作**: 扫描项目中的 Intent、Blueprint、Delivery
**输出**: 制品列表
**错误处理**: 无可追溯制品时提示使用 /ccc:init 创建制品并用 /ccc:link 建立链接；制品链接缺失时记录警告并继续处理其他制品

### Step 3: Generate Traceability Matrix
**目标**: 生成完整的可追溯性矩阵
**操作**: 映射需求到实现的完整链路
**输出**: 可追溯性矩阵
**错误处理**: 矩阵生成失败时显示错误并提供部分矩阵；需求映射不完整时标记缺口并在报告中突出显示

### Step 4: Analyze Coverage
**目标**: 分析覆盖率
**操作**: 计算追溯覆盖百分比和缺口
**输出**: 覆盖率分析报告
**错误处理**: 分析失败时使用基础统计并记录警告；数据不一致时进行数据清洗并标注可信度

### Step 5: Write Report
**目标**: 输出追溯报告
**操作**: 生成报告文件
**输出**: docs/traces/ 下的报告文件
**错误处理**: 输出目录缺失时自动创建 docs/traces/ 目录；文件写入权限被拒时显示权限错误并建议手动创建目录

### File Access

```bash
# View the generated report
cat docs/traces/YYYY-MM-DD-<project-id>-trace.md

# List all traceability reports
ls -la docs/traces/
```

## Error Handling

### Common Errors

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `TRACE-GEN-001` | Project not found | Verify project ID exists |
| `TRACE-GEN-002` | No traceable artifacts | Create artifacts with proper links |
| `TRACE-GEN-003` | Output directory missing | Create `docs/traces/` directory |
| `TRACE-GEN-004` | File write permission denied | Check directory permissions |

### Error Messages

```
❌ Error: Project 'invalid-project' not found
   → Use '/ccc:projects' to list available projects

❌ Error: No traceable artifacts in project 'my-project'
   → Create artifacts with '/ccc:init' and link with '/ccc:link'

❌ Error: Cannot create output directory 'docs/traces/'
   → Check permissions or create directory manually

❌ Error: Permission denied writing trace report
   → Check write permissions for 'docs/traces/' directory
```

### Recovery Steps

1. **Verify project**: `/ccc:projects`
2. **Check artifacts**: `/ccc:list --project-id=<id>`
3. **Create output directory**: `mkdir -p docs/traces/`
4. **Generate partial trace**: `/ccc:trace <project-id> --partial`
5. **Export to alternative location**: `/ccc:trace <project-id> --output=/tmp/trace.md`
