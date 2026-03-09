---
name: ccc:status
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

## Error Handling

| Error Scenario | Handling Strategy |
|----------------|-------------------|
| Project not found | Display available projects or suggest init |
| Corrupted state file | Display error, suggest manual state recovery |
| Missing artifact reference | Mark as "orphaned" in status display |
| Permission denied | Display helpful message about read permissions |
