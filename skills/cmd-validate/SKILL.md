---
name: ccc:validate
model: sonnet
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
description: "Validates artifacts using external tools including YAML lint, schema validation, and token count analysis"
argument-hint: "[--artifact-id=current] [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:validate

Runs external validation (YAML lint, schema, token count).

## Usage

```bash
/ccc:validate --artifact-id=BLP-001
/ccc:validate --artifact-id=BLP-001 --lang=en-us
```

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |

## Output Specification

### Console Output

```
Validation Report: BLP-001

✓ YAML syntax valid
✓ Schema compliant
✓ Token budget: 2,456 / 4,000
✓ All required fields present
✓ Cross-references valid

Status: PASSED
```

### File Output

| Attribute | Value |
|-----------|-------|
| **Directory** | `docs/validations/` |
| **Filename** | `YYYY-MM-DD-<artifact-id>-validation.md` |
| **Format** | Markdown |
| **Overwrite** | No (timestamp ensures uniqueness) |

**Example:**
- `/ccc:validate --artifact-id=BLP-001` → `docs/validations/2026-03-02-BLP-001-validation.md`

### Report Structure

| Section | Content |
|---------|---------|
| Overview | Artifact validated, validation date |
| YAML Validation | Syntax check results |
| Schema Compliance | Schema validation results |
| Token Budget | Token count and limit |
| Cross-References | Reference integrity check |
| Summary | Overall status and issues |

## Error Handling

| Error Scenario | Handling Strategy |
|----------------|-------------------|
| Artifact not found | Display available artifacts for selection |
| YAML syntax error | Display error with line number and suggestion |
| Schema validation failure | List specific violations with fix suggestions |
| External tool unavailable | Skip that check, note in report |
| Token limit exceeded | Warn and suggest splitting component |

### File Access

```bash
# View the generated report
cat docs/validations/YYYY-MM-DD-<artifact-id>-validation.md

# List all validation reports
ls -la docs/validations/
```
