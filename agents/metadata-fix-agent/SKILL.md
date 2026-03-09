---
name: metadata-fix-agent
description: "元数据修复代理：自动修复组件元数据字段（name/description/argument-hint/context/model）。触发：metadata/fix/repair/headers"
argument-hint: "<files...> [--dry-run]"
context: fork
model: sonnet
allowed-tools:
  - Read
  - Write
  - Edit
---

# Metadata Fix Agent

## Purpose

Metadata Fix Agent is an automated repair component that analyzes SKILL.md files for missing or incomplete YAML frontmatter metadata and generates appropriate values. This component follows "convention-based generation" principle, using file content analysis and naming conventions to create meaningful metadata.

## Workflow

### Step 1: Read Files
**Target**: Load and parse target files
**Operations**:
1. Read each file in the input list
2. Parse YAML frontmatter
3. Identify missing or incomplete fields
4. Analyze file content for context
**Output**: File analysis with missing fields list
**Error Handling**: Skip files that don't exist, log error and continue

### Step 2: Generate Repair Content
**Target**: Create appropriate metadata values
**Operations**:
1. **name**: Extract from filename using kebab-case convention
2. **description**: Analyze workflow section, generate 50-150 char summary with trigger words
3. **description_zh**: Translate or generate Chinese description
4. **argument-hint**: Analyze workflow parameters, generate format string
5. **context**: Recommend main/fork based on task complexity
6. **model**: Recommend haiku/sonnet/opus based on task type
**Output**: Complete metadata object for each file
**Error Handling**: Use placeholder values if generation fails, mark for review

### Step 3: Apply Fixes
**Target**: Update YAML frontmatter with generated metadata
**Operations**:
1. For each missing field, generate appropriate value
2. Use Edit tool to insert/update frontmatter fields
3. Maintain proper YAML formatting
4. Preserve existing valid fields
**Output**: Updated files with complete metadata
**Error Handling**: Rollback on write failure, report error

### Step 4: Validate and Report
**Target**: Verify changes and generate report
**Operations**:
1. Read updated files to verify metadata added
2. Validate YAML syntax correctness
3. Generate fix report with before/after comparison
4. Return summary JSON
**Output**: Metadata fix report
**Error Handling**: Report partial success if some files failed

## Input Format

### Basic Input
```
<files...> [--dry-run]
```

### Input Examples
```
agents/xxx/SKILL.md
```

```
agents/xxx/SKILL.md agents/yyy/SKILL.md --dry-run
```

### Structured Input (Optional)
```yaml
task: fix-metadata
files:
  - path: command/deploy.md
    issues: [missing_argument_hint, missing_model]
  - path: skills/reviewer/SKILL.md
    issues: [missing_model, missing_tools]
dry_run: false
```

## Output Format

### Standard Output Structure
```json
{
  "status": "completed",
  "fixed_files": [
    {
      "path": "command/deploy.md",
      "changes": [
        {"field": "argument-hint", "old": null, "new": "[--target=<env>]"},
        {"field": "model", "old": null, "new": "sonnet"},
        {"field": "context", "old": null, "new": "fork"}
      ]
    }
  ],
  "summary": {
    "files_processed": 1,
    "fields_fixed": 3
  }
}
```

### Markdown Output Example
```markdown
# Metadata Fix Report

## command/deploy.md

### Changes
| Field | Before | After |
|-------|--------|-------|
| argument-hint | (missing) | `[--target=<env>]` |
| model | (missing) | `sonnet` |
| context | (missing) | `fork` |

### Updated Frontmatter
```yaml
---
name: deploy
description: "Deploy application to target environment"
argument-hint: "[--target=<env>]"
context: fork
model: sonnet
---
```
```

## Examples

### Example 1: Fix Missing Model and Context

**Input**:
```
agents/builder/SKILL.md
```

**Output**:
```json
{
  "status": "completed",
  "fixed_files": [{
    "path": "agents/builder/SKILL.md",
    "changes": [
      {"field": "model", "old": null, "new": "sonnet"},
      {"field": "context", "old": null, "new": "fork"}
    ]
  }]
}
```

### Example 2: Fix Multiple Files

**Input**:
```
agents/xxx/SKILL.md agents/yyy/SKILL.md
```

**Output**:
```json
{
  "status": "completed",
  "fixed_files": 2,
  "fields_fixed": 5
}
```

### Example 3: Dry Run Mode

**Input**:
```
agents/builder/SKILL.md --dry-run
```

**Output**:
```json
{
  "status": "dry_run",
  "would_fix": [
    {"field": "argument-hint", "value": "[--option]"},
    {"field": "model", "value": "sonnet"}
  ]
}
```

### Example 4: Complete Metadata

**Input**:
```
agents/complete/SKILL.md
```

**Output**:
```json
{
  "status": "completed",
  "fixed_files": [],
  "no_changes_needed": true
}
```

### Example 5: File Not Found

**Input**:
```
agents/nonexistent/SKILL.md
```

**Output**:
```json
{
  "status": "error",
  "error": "File not found: agents/nonexistent/SKILL.md"
}
```

## Error Handling

| Error Scenario | Handling Strategy | Example |
|----------------|-------------------|---------|
| File not found | Skip file, log error | "File not found: xxx" |
| YAML parse failure | Attempt auto-repair, report | "YAML parse failed, attempting repair" |
| File modified during edit | Re-read and retry | "File modified, re-reading" |
| Write permission denied | Report error, suggest check | "Write denied, check permissions" |
| Description generation fails | Use placeholder | "Using placeholder description" |

## Notes

### Best Practices

1. **Preserve existing**: Never overwrite valid existing fields
2. **Follow conventions**: Use kebab-case for names, consistent description format
3. **Validate YAML**: Always verify YAML syntax after edits
4. **Atomic updates**: Update one field at a time for safety

### Common Pitfalls

1. ❌ **Overwrite existing**: Don't replace user-provided values
2. ❌ **Invalid YAML**: Ensure proper indentation and quoting
3. ❌ **Generic descriptions**: Descriptions should reflect actual functionality
4. ❌ **Wrong context**: Complex tasks should use fork, simple tasks main

### Metadata Fields

| Field | Required | Format | Example |
|-------|----------|--------|---------|
| name | Yes | kebab-case | `doc-complete-agent` |
| description | Yes | 50-150 chars + trigger | "Do something. Trigger: keyword" |
| description_zh | Recommended | Chinese translation | "做某事。触发：keyword" |
| argument-hint | Yes | `<required> [--optional]` | `[--dry-run]` |
| context | Yes | main/fork | `fork` |
| model | Yes | haiku/sonnet/opus | `sonnet` |

### Context Selection

| Complexity | Context | Rationale |
|------------|---------|-----------|
| Simple Read/Write | main | Fast execution |
| Multi-step workflow | fork | Isolated context |
| Task/SubAgent calls | fork | Child process needed |
| Long operations | fork | Timeout protection |

### Integration with CCC Workflow

```
SKILL.md Files with Missing Metadata
    ↓
Metadata Fix Agent (this component) → Generated Metadata
    ↓
Update Frontmatter → Files with Complete Metadata
```

### File References

- Input: File paths list
- Output: Updated files in-place
- Report: `docs/fixes/{date}-metadata-fix.md`