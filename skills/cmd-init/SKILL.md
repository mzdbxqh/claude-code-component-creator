---
name: ccc:cmd-init
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

## Examples

### Example 1: 创建简单的工具类 Skill

```bash
/ccc:init "我想创建一个 Skill 来快速查找项目中的 TODO 注释"
```

**输入**: 简单明确的需求描述

**执行过程**:
1. 分析需求，识别核心功能（搜索 TODO）
2. 推断组件类型为 Skill（单一工具功能）
3. 提取约束条件（支持多文件类型、输出格式友好）
4. 生成 Intent 制品

**输出**:
```
Intent created: INT-2026-03-07-001

Key decisions:
- Component type: Skill (auto-inferred)
- Workflow pattern: Search-Filter-Sort
- Hard constraints: 3 defined
- Complexity: simple

Quality score: 89/100
Next: Run /ccc:design to generate Blueprint
```

**生成文件**: `docs/ccc/intent/2026-03-07-INT-001.yaml`

### Example 2: 创建复杂的多阶段工具

```bash
/ccc:init "我要做一个自动部署工具，支持 Kubernetes 和 Docker，需要配置验证和回滚功能"
```

**场景**: 复杂需求包含多个子系统和约束

**执行过程**:
1. 识别多个功能域（部署、验证、回滚）
2. 推断组件类型为 Skill + Hook 组合
3. 提取硬约束（支持 K8s/Docker）和软约束（易用性）
4. 设计决策记录（为什么选择特定架构）

**输出**:
```
Intent created: INT-2026-03-07-002

Key decisions:
- Component type: Skill + Hook (auto-inferred)
- Workflow pattern: Pipeline with rollback
- Hard constraints: 5 defined
- Complexity: complex

Quality score: 92/100
Next: Run /ccc:design to generate Blueprint
```

### Example 3: 多语言支持（英文输出）

```bash
/ccc:init "I want to create a code review assistant that checks style and suggests improvements" --lang=en-us
```

**用例**: 英文需求，指定英文输出

**输出**:
```
Intent created: INT-2026-03-07-003

Key decisions:
- Component type: Skill (auto-inferred)
- Workflow pattern: Analysis-Feedback
- Hard constraints: 4 defined

Quality score: 85/100
Next: Run /ccc:design to generate Blueprint
```

### Example 4: 交互式输入（未提供描述）

```bash
/ccc:init
```

**场景**: 直接运行命令不带参数

**执行过程**:
```
Please describe what you want to create:
> [User types: "我想创建一个日志分析工具"]

Analyzing requirement...

Intent created: INT-2026-03-07-004
...
```

### Example 5: 处理质量分数过低的情况

```bash
/ccc:init "做个东西"
```

**场景**: 需求描述过于模糊

**输出**:
```
Intent created: INT-2026-03-07-005

Warning: Quality score below threshold
Quality score: 45/100

Issues detected:
- Requirement too vague (no clear objective)
- Missing constraints
- Component type unclear

Suggestion: Please provide more details:
1. What specific problem does it solve?
2. What are the expected inputs and outputs?
3. Are there any technical constraints?

You can run /ccc:init again with a clearer description.
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
