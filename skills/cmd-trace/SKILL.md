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
