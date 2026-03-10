---
name: ccc:cmd-status
model: sonnet
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
description: "Displays current project workflow state and artifact status including intent, blueprint, and delivery progress with stage indicators"
argument-hint: "[--project-id=current] [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:status

Shows current workflow state and artifact status.

## Usage

```bash
/ccc:status              # Show current project status
/ccc:status --project-id=my-project
/ccc:status --lang=en-us # Show status in English
```

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |

## Output Specification

### Console Output

```
Project: my-project
Status: in_progress (blueprint stage)

Artifacts:
├─ Intent: INT-2026-03-01-001 [completed]
├─ Blueprint: BLP-2026-03-01-002 [in_progress]
└─ Delivery: Not started

Progress: 40%
Next action: Run /ccc:design to complete Blueprint
```

### File Output

| Attribute | Value |
|-----------|-------|
| **Directory** | `docs/ccc/status/` |
| **Filename** | `YYYY-MM-DD-<project-id>-status.md` |
| **Format** | Markdown |
| **Overwrite** | Yes (updated on each status check) |

**Example:**
- `/ccc:status --project-id=my-project` → `docs/ccc/status/my-project-status.md`

### Report Structure

| Section | Content |
|---------|---------|
| Overview | Project name, status date, current stage |
| Artifacts | List of all artifacts with status |
| Progress | Percentage completion and stage indicator |
| Next Actions | Recommended next steps |

### File Access

```bash
# View the status report
cat docs/ccc/status/<project-id>-status.md

# List all status reports
ls -la docs/ccc/status/
```

## Examples

### Example 1: 查看当前项目状态

```bash
/ccc:status
```

**场景**: 查看正在进行中的项目整体进度

**输出**:
```
Project: current-workspace
Status: in_progress (blueprint stage)

Workflow Progress:
┌─────────────────────────────────────────────────────┐
│ Intent ━━━━━━━━●━━━━━━━━ Blueprint ············· Delivery │
│  [completed]      [in_progress]        [pending]   │
└─────────────────────────────────────────────────────┘

Artifacts:
├─ Intent: INT-2026-03-01-001 [completed]
│  Created: 2026-03-01 10:23:45
│  Quality: 89/100
│
├─ Blueprint: BLP-2026-03-01-002 [in_progress]
│  Created: 2026-03-01 10:45:12
│  Quality: --/100 (not finalized)
│
└─ Delivery: Not started

Progress: 40%
Next action: Run /ccc:design to complete Blueprint
```

### Example 2: 查看特定项目状态

```bash
/ccc:status --project-id=deploy-tool
```

**场景**: 在多项目工作区查看特定项目的状态

**输出**:
```
Project: deploy-tool
Status: completed (all stages)

Workflow Progress:
┌─────────────────────────────────────────────────────┐
│ Intent ━━━━━●━━━━━ Blueprint ━━━━━●━━━━━ Delivery   │
│  [completed]      [completed]         [completed]   │
└─────────────────────────────────────────────────────┘

Artifacts:
├─ Intent: INT-2026-02-28-005 [completed]
│  Created: 2026-02-28 14:20:30
│  Quality: 92/100
│
├─ Blueprint: BLP-2026-02-28-006 [completed]
│  Created: 2026-02-28 15:10:45
│  Quality: 94/100
│  Iterations: 2 (from BLP-005 → BLP-006)
│
└─ Delivery: DLV-2026-02-28-007 [completed]
   Created: 2026-02-28 16:05:22
   Compliance: 90/100
   Files: 5 generated

Progress: 100%
Status: ✅ Project complete
```

### Example 3: 多语言支持（英文）

```bash
/ccc:status --lang=en-us
```

**输出**:
```
Project: current-workspace
Status: blueprint_stage

Workflow Progress:
┌─────────────────────────────────────────────────────┐
│ Intent ━━━━━━━━●━━━━━━━━ Blueprint ············· Delivery │
│  [completed]      [in_progress]        [pending]   │
└─────────────────────────────────────────────────────┘

Artifacts:
├─ Intent: INT-2026-03-01-001 [completed]
├─ Blueprint: BLP-2026-03-01-002 [in_progress]
└─ Delivery: Not started

Progress: 40%
Next action: Run /ccc:design to complete Blueprint
```

### Example 4: 空工作区（无项目）

```bash
/ccc:status
```

**场景**: 首次使用或新的工作目录

**输出**:
```
No active project found in current workspace.

Available projects:
  (none)

To start a new project:
  1. Run /ccc:init "your requirement description"
  2. Or run /ccc:quick "your requirement" for one-step creation

Example:
  /ccc:init "我想创建一个日志分析工具"
```

### Example 5: 检测到孤立制品

```bash
/ccc:status
```

**场景**: 工作流中断导致制品关系不完整

**输出**:
```
Project: interrupted-workflow
Status: inconsistent (orphaned artifacts detected)

Workflow Progress:
┌─────────────────────────────────────────────────────┐
│ Intent ━━━━━━━━●━━━━━━━━ Blueprint ···⚠··· Delivery │
│  [completed]      [orphaned]          [missing]     │
└─────────────────────────────────────────────────────┘

Artifacts:
├─ Intent: INT-2026-03-05-003 [completed]
│  Created: 2026-03-05 09:15:20
│  Quality: 87/100
│
├─ Blueprint: BLP-2026-03-05-004 [orphaned] ⚠
│  Created: 2026-03-05 09:40:55
│  Issue: Referenced intent INT-2026-03-05-999 not found
│
└─ Delivery: Not started

⚠ Inconsistency detected

Recovery options:
  1. Create new Blueprint: /ccc:design --intent-id=INT-2026-03-05-003
  2. Manual inspection: cat docs/ccc/blueprint/2026-03-05-BLP-004.yaml
  3. Clean workspace: /ccc:clean --confirm
```

### Example 6: 查看已完成项目的历史

```bash
/ccc:status --project-id=log-parser
```

**输出**:
```
Project: log-parser
Status: completed (archived)

Workflow Progress:
┌─────────────────────────────────────────────────────┐
│ Intent ━━━━━●━━━━━ Blueprint ━━━━━●━━━━━ Delivery   │
│  [completed]      [completed]         [completed]   │
└─────────────────────────────────────────────────────┘

Artifacts:
├─ Intent: INT-2026-02-20-001 [completed]
├─ Blueprint: BLP-2026-02-20-003 [completed]
│  (Iterations: BLP-001 → BLP-002 → BLP-003)
└─ Delivery: DLV-2026-02-20-004 [completed]

Progress: 100%
Delivery location: docs/ccc/delivery/2026-02-20-DLV-004/

Status report saved: docs/ccc/status/log-parser-status.md
```

## Error Handling

| Error Scenario | Handling Strategy |
|----------------|-------------------|
| Project not found | Display available projects or suggest init |
| Corrupted state file | Display error, suggest manual state recovery |
| Missing artifact reference | Mark as "orphaned" in status display |
| Permission denied | Display helpful message about read permissions |
