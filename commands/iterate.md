---
name: ccc:iterate
model: sonnet
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
description: "Iterates on existing blueprint artifacts to create improved versions with refinement tracking and change documentation"
argument-hint: "[--artifact-id=<id>] [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:iterate

Iterates on an existing blueprint artifact, creating a new version with improvements.

## Usage

```bash
/ccc:iterate --artifact-id=BLP-001
/ccc:iterate --artifact-id=BLP-001 --lang=en-us
```

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |

## Workflow

1. Load the specified artifact (or current context artifact)
2. Analyze the artifact for improvement opportunities
3. Apply refinements based on feedback or detected issues
4. Generate a new artifact with incremented ID (e.g., BLP-001 → BLP-002)
5. Create iteration report documenting changes

## Output Specification

### Console Output

```
Iteration Complete: BLP-001 → BLP-002

Changes Applied:
  ✓ Updated workflow steps
  ✓ Added error handling
  ✓ Refined tool selection

New Artifact: BLP-002
Status: READY for build

Iteration report: docs/iterations/2026-03-02-BLP-001-iteration.md
```

### File Output

| Attribute | Value |
|-----------|-------|
| **Directory** | `docs/iterations/` |
| **Filename** | `YYYY-MM-DD-<artifact-id>-iteration.md` |
| **Format** | Markdown |
| **Overwrite** | No (timestamp ensures uniqueness) |

**Example:**
- `/ccc:iterate --artifact-id=BLP-001` → `docs/iterations/2026-03-02-BLP-001-iteration.md`

### Artifact Output

| Attribute | Value |
|-----------|-------|
| **Directory** | `docs/ccc/blueprint/` |
| **Filename** | `YYYY-MM-DD-<new-artifact-id>.yaml` |
| **Format** | YAML |

### Report Structure

| Section | Content |
|---------|---------|
| Overview | Source artifact, iteration date, new artifact ID |
| Changes | List of modifications made |
| Rationale | Why changes were needed |
| Previous Artifact | Reference to BLP-001 |
| New Artifact | Reference to BLP-002 |
| Summary | Status and next steps |

## Error Handling

| Error Scenario | Handling Strategy |
|----------------|-------------------|
| Artifact not found | Display available artifacts and suggest selection |
| No improvements detected | Report "No changes needed" and exit gracefully |
| Invalid artifact type for iteration | Display supported types (only Blueprint) |
| File generation failure | Display specific error and rollback changes |
| Permission denied | Display helpful message about file permissions |

### File Access

```bash
# View the iteration report
cat docs/iterations/YYYY-MM-DD-<artifact-id>-iteration.md

# View the new blueprint artifact
cat docs/ccc/blueprint/YYYY-MM-DD-<new-artifact-id>.yaml

# List all iteration reports
ls -la docs/iterations/
```
