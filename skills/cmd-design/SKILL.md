---
name: ccc:cmd-design
model: sonnet
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
description: "Creates comprehensive blueprint artifacts from intent specifications using structured 5-stage design workflow analysis"
argument-hint: "--name=<name> [--intent-id=current] [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:design

Creates a blueprint from intent through a 5-stage workflow.

## Usage

```bash
/ccc:design --name=deploy-skill
/ccc:design --name=api-service --intent-id=INT-001
/ccc:design --name=api-service --intent-id=INT-001 --lang=en-us
```

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |

## Workflow

1. **Analyze Intent** - Parse requirements and constraints
2. **Design Workflow** - Create execution flow
3. **Select Tools** - Choose appropriate tools
4. **Generate Evidence Chain** - Create traceability (capability→skill→status)
5. **Define Policies** - Set constraints and rules
6. **Generate Blueprint** - Create BLP artifact

## Output Specification

### Console Output

```
Design Complete: deploy-skill

Blueprint Generated: BLP-003
Status: READY for review

Design document: docs/designs/2026-03-02-deploy-skill-design.md
Blueprint artifact: docs/ccc/blueprint/2026-03-02-BLP-003.yaml
```

### File Output (Design Document)

| Attribute | Value |
|-----------|-------|
| **Directory** | `docs/designs/` |
| **Filename** | `YYYY-MM-DD-<name>-design.md` |
| **Format** | Markdown |
| **Overwrite** | No (timestamp ensures uniqueness) |

**Example:**
- `/ccc:design --name=deploy-skill` → `docs/designs/2026-03-02-deploy-skill-design.md`

### Artifact Output (Blueprint)

| Attribute | Value |
|-----------|-------|
| **Directory** | `docs/ccc/blueprint/` |
| **Filename** | `YYYY-MM-DD-<artifact-id>.yaml` |
| **Format** | YAML |

### Design Document Structure

| Section | Content |
|---------|---------|
| Overview | Design name, date, requirements summary |
| Requirements | Functional and non-functional requirements |
| Design Decisions | Key architectural choices |
| Component Structure | High-level component breakdown |
| Workflow | Execution flow description |
| Evidence Chain | Capability table, Skill mapping, Verification checklist |
| Blueprint Reference | Link to BLP artifact |
| Next Steps | Recommended actions |

## Examples

### Example 1: Design a Deployment Skill

```bash
/ccc:design --name=deploy-skill
```

**Input**: Existing intent from `/ccc:init`

**Process**:
1. Analyzes intent for "automated deployment tool"
2. Determines component type: Skill + Hook combination
3. Designs workflow: Analyze → Validate → Deploy → Verify
4. Selects tools: Read, Write, Bash, Task
5. Generates blueprint with policies for rollback on failure

**Output Files**:
- `docs/designs/2026-03-02-deploy-skill-design.md`
- `docs/ccc/blueprint/2026-03-02-BLP-003.yaml`

### Example 2: Design with Specific Intent

```bash
/ccc:design --name=api-service --intent-id=INT-001
```

**Use Case**: When multiple intents exist, specify which one to use.

### Example 3: Design Iteration

```bash
# First design
/ccc:design --name=doc-reader

# Review and iterate on design
/ccc:review --artifact-id=BLP-001

# Create improved version
/ccc:design --name=doc-reader-v2 --intent-id=INT-001
```

## Error Handling

| Error Scenario | Handling Strategy |
|----------------|-------------------|
| Intent not found | Display available intents and suggest selection |
| Invalid intent format | Display validation error with details |
| Blueprint generation fails | Display error and suggest reviewing intent |
| File write failure | Display filesystem error with path |

### File Access

```bash
# View the design document
cat docs/designs/YYYY-MM-DD-<name>-design.md

# View the blueprint artifact
cat docs/ccc/blueprint/YYYY-MM-DD-<artifact-id>.yaml

# List all design documents
ls -la docs/designs/
```
