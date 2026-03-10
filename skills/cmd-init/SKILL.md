---
name: ccc:init
description: |
  Create Intent artifact using 4-question framework.
  Analyzes user requirement and generates structured Intent with cognitive load management.
  使用 4 问题框架创建 Intent 制品。
  分析用户需求并生成包含认知卸载的结构化 Intent。
model: sonnet
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
argument-hint: "[requirement-description] [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:init Command

## Usage

```bash
/ccc:init "我要做一个自动部署工具，支持 Kubernetes"
/ccc:init "I want to create an auto-deployment tool" --lang=en-us
/ccc:init "Kubernetes をサポートする自動デプロイツールを作成したい" --lang=ja-jp
```

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |

## Workflow

1. **Collect user input** - If no argument provided, prompt interactively
2. **Call intent-core** - Pass requirement to subagent with lang parameter
3. **Generate Intent** - Create artifact in `docs/ccc/intent/`
4. **Display summary** - Show key decisions and quality score in specified language
5. **Suggest next step** - Prompt to run `/ccc:design`

## Output Specification

### Console Output

```
Intent created: INT-2026-03-01-001

Key decisions:
- Component type: Skill (auto-inferred)
- Workflow pattern: Sequential
- Hard constraints: 3 defined

Quality score: 87/100
Next: Run /ccc:design to generate Blueprint
```

### File Output

| Attribute | Value |
|-----------|-------|
| **Directory** | `docs/ccc/intent/` |
| **Filename** | `YYYY-MM-DD-<artifact-id>.yaml` |
| **Format** | YAML |
| **Overwrite** | No (timestamp ensures uniqueness) |

**Example:**
- `/ccc:init "我要做一个自动部署工具"` → `docs/ccc/intent/2026-03-02-INT-001.yaml`

### Intent Structure

| Section | Content |
|---------|---------|
| artifact | Artifact ID, type, version |
| metadata | Name, description, creation date |
| requirements | Functional and non-functional requirements |
| constraints | Hard and soft constraints |
| decisions | Key design decisions and rationale |

### File Access

```bash
# View the generated intent artifact
cat docs/ccc/intent/YYYY-MM-DD-<artifact-id>.yaml

# List all intent artifacts
ls -la docs/ccc/intent/
```

## Error Handling

| Error Scenario | Handling Strategy |
|----------------|-------------------|
| No user input provided | Prompt interactively for requirement |
| Intent generation fails | Display error and suggest rephrasing |
| File write failure | Display filesystem error with path |
| Subagent timeout | Retry once, then fail with timeout message |

## Example Output

```
Intent created: INT-2026-03-01-001

Key decisions:
- Component type: Skill (auto-inferred)
- Workflow pattern: Sequential
- Hard constraints: 3 defined

Quality score: 87/100
Next: Run /ccc:design to generate Blueprint
```
