---
name: ccc:cmd-build
model: sonnet
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
description: "Generates complete production-ready deliverable packages from validated blueprints including SKILL.md, implementation code, tests, and documentation"
argument-hint: "--artifact-id=<blueprint-id> [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:build

Generates deliverable files from a blueprint artifact.

## Usage

```bash
/ccc:build --artifact-id=BLP-001
/ccc:build --artifact-id=BLP-001 --lang=en-us
```

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |

## Workflow

1. **Load Blueprint** - Read and parse the blueprint
2. **Generate SKILL.md** - Create skill definition
3. **Generate Implementation** - Create code files
4. **Generate Tests** - Create test files
5. **Package Delivery** - Create DLV artifact

## Output Specification

### Console Output

```
Build Complete: DLV-001

Files Generated: 5
  ✓ SKILL.md
  ✓ implementation/
  ✓ tests/
  ✓ README.md
  ✓ metadata.yaml

Status: SUCCESS

Build report: docs/ccc/delivery/2026-03-02-DLV-001/build-report.md
```

### File Output (Build Report)

| Attribute | Value |
|-----------|-------|
| **Directory** | `docs/ccc/delivery/YYYY-MM-DD-<artifact-id>/` |
| **Filename** | `build-report.md` |
| **Format** | Markdown |
| **Overwrite** | Yes (updated on rebuild) |

**Example:**
- `/ccc:build --artifact-id=BLP-001` → `docs/ccc/delivery/2026-03-02-DLV-001/build-report.md`

### Artifact Output (Delivery)

| Attribute | Value |
|-----------|-------|
| **Directory** | `docs/ccc/delivery/YYYY-MM-DD-<artifact-id>/` |
| **Contents** | Generated files (SKILL.md, implementation/, tests/, etc.) |
| **Format** | Mixed (Markdown, YAML, code files) |

### Build Report Structure

| Section | Content |
|---------|---------|
| Overview | Blueprint built, build date, delivery artifact ID |
| Build Status | Success/failure with details |
| Files Generated | List of created files |
| Verification Results | Tests passed, validation status |
| Source Blueprint | Reference to BLP artifact |
| Summary | Status and deployment readiness |

## Examples

### Example 1: Build a Simple Skill

```bash
/ccc:build --artifact-id=BLP-001
```

**Input**: Blueprint for a documentation reader skill

**Generated Output**:
```
docs/ccc/delivery/2026-03-02-DLV-001/
├── build-report.md
├── SKILL.md
├── metadata.yaml
├── README.md
└── implementation/
    └── (empty for pure skills)
```

**Console Output**:
```
Build Complete: DLV-001

Files Generated: 5
  ✓ SKILL.md
  ✓ implementation/
  ✓ tests/
  ✓ README.md
  ✓ metadata.yaml

Status: SUCCESS
Build report: docs/ccc/delivery/2026-03-02-DLV-001/build-report.md
```

### Example 2: Build Complex Multi-Component System

```bash
/ccc:build --artifact-id=BLP-005
```

**Input**: Blueprint with 3 subagents and 2 commands

**Generated Output**:
```
docs/ccc/delivery/2026-03-02-DLV-005/
├── build-report.md
├── README.md
├── agents/
│   ├── data-processor/SKILL.md
│   ├── validator/SKILL.md
│   └── reporter/SKILL.md
├── commands/
│   ├── process-data.md
│   └── generate-report.md
└── tests/
    ├── unit/
    └── integration/
```

### Example 3: Rebuild After Design Update

```bash
# Original build
/ccc:build --artifact-id=BLP-003

# Designer updates blueprint
/ccc:design --name=updated-skill --intent-id=INT-001

# Rebuild with same blueprint ID (overwrites delivery)
/ccc:build --artifact-id=BLP-003
```

## Error Handling

| Error Scenario | Handling Strategy |
|----------------|-------------------|
| Blueprint not found | Display available blueprints and suggest selection |
| Invalid blueprint ID | Display error with correct format example |
| File generation fails | Display specific file error and continue |
| Directory creation fails | Display permissions error |

### File Access

```bash
# View the build report
cat docs/ccc/delivery/YYYY-MM-DD-<artifact-id>/build-report.md

# List delivery files
ls -la docs/ccc/delivery/YYYY-MM-DD-<artifact-id>/

# View generated SKILL.md
cat docs/ccc/delivery/YYYY-MM-DD-<artifact-id>/SKILL.md
```
