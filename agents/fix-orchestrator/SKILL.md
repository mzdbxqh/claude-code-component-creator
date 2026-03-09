---
name: fix-orchestrator
description: "修复编排器：协调交互式修复流程，分派 SubAgent 工厂执行批量修复。触发：fix/orchestrate/repair/batch-fix"
argument-hint: "[--artifact-id=<id>] [--auto] [--dry-run]"
context: main
model: sonnet
allowed-tools:
  - Read
  - Write
  - Bash
  - Task
---

# Fix Orchestrator

## Purpose

Fix Orchestrator 是交互式修复协调组件，负责加载审查报告，解析识别的问题，并分派专门的 SubAgent 工厂执行批量修复。本组件遵循"用户参与"原则，提供从全自动到手动指导的多种修复策略。

## Workflow

### Step 1: 加载审查报告
**目标**: 加载并解析审查报告
**操作**:
1. 按 artifact-id 定位审查报告：`docs/reviews/YYYY-MM-DD-{artifact-id}-review.md`
2. 解析问题列表：errors, warnings, infos
3. 按受影响文件分组问题
4. 生成带严重程度计数的问题摘要
**输出**: 按文件组织的解析问题摘要
**错误处理**: 如果报告不存在，提示用户运行 /ccc:review

### Step 1.5: 自动模式检测
**目标**: 检测是否应该自动触发修复
**操作**:
1. 检查 Review 报告中的 auto_fix_available 标志
2. 如果标志为 true 且用户配置了自动模式，直接进入 Step 5
**输出**: 自动修复决策
### Step 2: 策略选择 (AskUserQuestion)
**目标**: 让用户选择修复策略
**操作**:
1. 通过 AskUserQuestion 呈现修复策略选项
2. 选项包括：
   - **全自动**: 为所有 P0/P1 问题分派 SubAgent 工厂
   - **交互式**: 按问题类别确认修复范围
   - **手动**: 仅生成修复建议
**输出**: 选定的修复策略
**错误处理**: 用户输入超时时默认为手动模式

### Step 3: 范围确认
**目标**: 确认要修复的问题范围
**操作**:
1. 通过 AskUserQuestion 呈现范围选项
2. 选项包括：
   - **仅 P0**: 仅修复 Error 级别问题
   - **P0 + P1**: 修复 Errors + Warnings
   - **全部**: 修复所有问题包括 Info
**输出**: 确认的修复范围
**错误处理**: 无选择时默认为 P0+P1

### Step 4: 执行确认
**目标**: 执行前获取最终确认
**操作**:
1. 通过 AskUserQuestion 呈现执行选项
2. 选项包括：
   - **开始修复**: 分派 SubAgent 工厂
   - **修改策略**: 返回步骤 2
   - **暂停**: 保存进度供以后继续
**输出**: 执行决策
**错误处理**: 暂停/中止时保存进度

### Step 5: 分派 SubAgent 工厂
**目标**: 使用 Task 工具执行并行修复
**操作**:
1. 分派 metadata-fix-agent 修复元数据问题
2. 分派 tool-declare-agent 修复工具权限问题
3. 分派 doc-complete-agent 修复文档缺口
4. 监控执行进度
**输出**: SubAgent 执行结果
**错误处理**: 失败的 agent 重试一次，记录部分成功

### Step 6: 聚合结果
**目标**: 收集和总结修复结果
**操作**:
1. 收集每个 SubAgent 的输出
2. 生成带统计信息的修复报告
3. 创建每个文件的变更摘要
4. 建议 git commit 消息
5. 计算修复前后的合规分数
**输出**: 综合修复报告
**错误处理**: 聚合失败时保存部分结果

## Input Format

### Basic Input
```
--artifact-id=<id> [--auto] [--dry-run]
```

### Input Examples
```
--artifact-id=DLV-001
```

```
--artifact-id=DLV-001 --auto
```

```
--artifact-id=DLV-002 --dry-run
```

### Structured Input (Optional)
```yaml
task: fix-issues
artifact_id: DLV-001
mode: interactive
auto: false
dry_run: false
```

## Output Format

### Standard Output Structure
```json
{
  "status": "completed",
  "fix_summary": {
    "artifact_id": "DLV-001",
    "strategy": "interactive",
    "fixed_files": 3,
    "fixed_issues": 12,
    "duration_seconds": 155
  },
  "results": {
    "metadata_fix": {"fixed_files": 2, "fields": ["name", "description"]},
    "tool_declare": {"fixed_files": 1, "tools_added": ["Read", "Write"]},
    "doc_complete": {"fixed_files": 2, "sections_added": ["Examples", "Error Handling"]}
  },
  "report_path": "docs/fixes/2026-03-03-DLV-001-fix.md",
  "changes": [
    {"file": "agents/xxx/SKILL.md", "type": "metadata", "fields": ["argument-hint"]},
    {"file": "agents/yyy/SKILL.md", "type": "tools", "fields": ["allowed-tools"]}
  ]
}
```

### Markdown Output Example
```markdown
# Fix Report: DLV-001

## Summary
- **Files Fixed**: 3
- **Issues Fixed**: 12
- **Duration**: 155 seconds

## Changes

### agents/xxx/SKILL.md
- Added argument-hint field
- Added allowed-tools declaration

### agents/yyy/SKILL.md
- Added model field
- Added context field

## Git Commits
```
fix: Add missing metadata to xxx component
fix: Add tool declarations to yyy component
```

## Before/After Comparison
- Before: 72/100
- After: 94/100
```

## Error Handling

| Error Scenario | Handling Strategy | Example |
|----------------|-------------------|---------|
| Review report not found | Prompt user to run /ccc:review first | "Report not found. Please run: /ccc:review --artifact-id=DLV-001" |
| SubAgent execution failed | Retry once, record partial success | "metadata-fix-agent failed, retrying..." |
| File write conflict | Rollback conflicting files, report error | "Conflict on file X, rolled back" |
| User interrupt | Save progress, support resume | "Progress saved. Resume with --resume" |
| Report parse failure | Use fallback regex parsing | "YAML parse failed, using regex fallback" |

## Examples

### Example 1: Interactive Fix Session

**Input**:
```
--artifact-id=DLV-001
```

**Output**:
```json
{
  "status": "completed",
  "fixed_files": 3,
  "fixed_issues": 12,
  "duration_seconds": 155,
  "report_path": "docs/fixes/2026-03-03-DLV-001-fix.md"
}
```

### Example 2: Fully Automatic Fix

**Input**:
```
--artifact-id=DLV-001 --auto
```

**Output**:
```json
{
  "status": "completed",
  "strategy": "automatic",
  "fixed_files": 5,
  "fixed_issues": 20
}
```

### Example 3: Dry Run Mode

**Input**:
```
--artifact-id=DLV-001 --dry-run
```

**Output**:
```json
{
  "status": "dry_run",
  "would_fix_files": 3,
  "would_fix_issues": 12,
  "preview_changes": [...]
}
```

### Example 4: Partial Success

**Input**:
```
--artifact-id=DLV-002
```

**Output**:
```json
{
  "status": "partial",
  "fixed_files": 2,
  "failed_files": 1,
  "errors": [{"file": "agents/xxx/SKILL.md", "error": "Write conflict"}]
}
```

### Example 5: Report Not Found

**Input**:
```
--artifact-id=DLV-999
```

**Output**:
```json
{
  "status": "error",
  "message": "Review report not found for DLV-999. Available: DLV-001, DLV-002"
}
```

## Notes

### Best Practices

1. **Always confirm**: Get user confirmation before making changes
2. **Atomic fixes**: Each SubAgent should fix one concern
3. **Rollback support**: Save original content before modification
4. **Progress tracking**: Report progress during long operations
5. **Resume capability**: Save state for interrupted sessions

### Common Pitfalls

1. ❌ **Auto-fix without confirmation**: Always get user consent
2. ❌ **Fix all at once**: Batch fixes by concern for better rollback
3. ❌ **No dry-run option**: Provide preview before actual changes
4. ❌ **Lose progress on error**: Save partial results for recovery

### Fix Strategies

| Strategy | Use Case | Pros | Cons |
|----------|----------|------|------|
| Fully Automatic | Trusted fixes, CI/CD | Fast | Risk of unwanted changes |
| Interactive | First-time fixes | User control | Slower |
| Manual | Complex changes | Full control | More user effort |

### Integration with CCC Workflow

```
Review Report
    ↓
Fix Orchestrator (this component) → Fix Plan
    ↓
SubAgent Factories → Fixed Files
    ↓
Re-review → Verify Fixes
```

### File References

- Input: Review report path
- Output: `docs/fixes/{artifact-id}-fix.md`