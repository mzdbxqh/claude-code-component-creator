---
name: cmd-init
description: "开发流程第1步。4问框架分析需求，创建Intent制品。触发：启动/初始化/需求。输出Intent给design。"
model: sonnet
context: fork
disable-model-invocation: true
allowed-tools: [Read, Write, Edit, Glob, Grep]
argument-hint: "[requirement-description] [--lang=zh-cn|en-us|ja-jp]"
skills:
  - ccc:workflow-engine
---

# /cmd-init

**开发流程**: **init** → `design` → `implement` → `review` → `fix` → `validate` → `build`

Create Intent artifact using 4-question framework. Analyzes user requirement and generates structured Intent with cognitive load management.

## 模型要求

- **推荐**: Claude Sonnet 4.5+ (高效能,最佳性价比)
- **可用**: Claude Opus 4.5+ (最高质量,复杂需求分析)
- **最小**: Claude Sonnet 4.5+ (最低要求)

### 功能需求
- 需要支持 Tool Use (Read, Write, Edit, Glob, Grep)
- 需要支持多轮对话和需求澄清
- 需要使用 4 问框架进行需求分析
- 建议上下文窗口 >= 100K tokens

## Usage

```bash
/cmd-init "我要做一个自动部署工具，支持 Kubernetes"
/cmd-init "I want to create an auto-deployment tool" --lang=en-us
/cmd-init "Kubernetes をサポートする自動デプロイツールを作成したい" --lang=ja-jp
```

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |

## SubAgents 协作

本工作流使用以下 SubAgents 进行任务分解和执行：

### 核心 Agents
- **ccc:intent-core**: 意图分析和需求澄清核心，使用 4 问框架提取用户需求

### 调度策略
- **串行执行**: cmd-init → ccc:intent-core
- **并行执行**: 无（单一 agent 执行）
- **错误处理**: agent 失败时提示用户补充信息并重试

### Agent 输入输出
| Agent | 输入 | 输出 |
|-------|------|------|
| ccc:intent-core | 用户需求描述 + lang 参数 | Intent YAML 制品 |

### 调用示例
```
用户: /cmd-init "我要做一个自动部署工具"
  ↓
cmd-init 接收参数
  ↓
调用 ccc:intent-core (requirement="我要做一个自动部署工具", lang="zh-cn")
  ↓
ccc:intent-core 执行 4 问框架分析
  ↓
生成 Intent 制品: docs/ccc/intent/2026-03-02-INT-001.yaml
  ↓
cmd-init 输出摘要和下一步建议
```

## Workflow

1. **Collect user input** - If no argument provided, prompt interactively
2. **Call intent-core** - Pass requirement to subagent with lang parameter
3. **Generate Intent** - Create artifact in `docs/ccc/intent/`
4. **Display summary** - Show key decisions and quality score in specified language
5. **Suggest next step** - Prompt to run `/cmd-design`

## Output Specification

### Console Output

```
Intent created: INT-2026-03-01-001

Key decisions:
- Component type: Skill (auto-inferred)
- Workflow pattern: Sequential
- Hard constraints: 3 defined

Quality score: 87/100
Next: Run /cmd-design to generate Blueprint
```

### File Output

| Attribute | Value |
|-----------|-------|
| **Directory** | `docs/ccc/intent/` |
| **Filename** | `YYYY-MM-DD-<artifact-id>.yaml` |
| **Format** | YAML |
| **Overwrite** | No (timestamp ensures uniqueness) |

**Example:**
- `/cmd-init "我要做一个自动部署工具"` → `docs/ccc/intent/2026-03-02-INT-001.yaml`

### Intent Structure

**YAML文件结构**（完整示例）:

```yaml
# Intent制品完整结构
version: "3.0"
id: "INT-2026-03-07-001"
type: "intent"
created_at: "2026-03-07T14:30:00Z"

# 元数据
metadata:
  name: "todo-finder"
  description: "快速查找项目中的 TODO 注释"
  component_type: "skill"  # skill | command | agent | hook
  complexity: "simple"      # simple | medium | complex
  priority: "high"          # low | medium | high | critical

# 功能需求
requirements:
  functional:
    - "扫描项目文件查找 TODO/FIXME/HACK 注释"
    - "支持多种文件类型（.js, .py, .java, .md）"
    - "按优先级和文件分组显示结果"
    - "提供行号和代码上下文"

  non_functional:
    performance:
      - "扫描速度: <3秒（1000文件）"
      - "内存占用: <100MB"

    security:
      - "仅读取权限，不修改文件"
      - "排除 .git 和 node_modules 目录"

    usability:
      - "输出格式友好，易于阅读"
      - "支持颜色高亮"

# 约束条件
constraints:
  hard:
    - "必须使用 Bash 工具执行文件搜索"
    - "必须处理空结果情况"
    - "文件路径必须使用相对路径"

  soft:
    - "建议支持自定义关键词"
    - "建议支持输出到文件"
    - "建议显示统计摘要"

# 设计决策
decisions:
  - id: "DEC-001"
    decision: "选择 Skill 组件类型"
    rationale: "单一工具功能，用户主动触发，不需要工作流编排"
    alternatives: ["Command", "Subagent"]
    selected: "Skill"

  - id: "DEC-002"
    decision: "使用 grep/rg 工具搜索"
    rationale: "性能优异，正则表达式支持强"
    alternatives: ["find + cat", "Node.js脚本"]
    selected: "grep/rg"

  - id: "DEC-003"
    decision: "输出格式使用 Markdown"
    rationale: "与 Claude Code 环境一致，易于阅读"
    alternatives: ["JSON", "Plain text"]
    selected: "Markdown"

# 工作流模式
workflow_pattern: "search-filter-sort"
workflow_stages:
  - name: "scan"
    description: "扫描文件系统"
  - name: "filter"
    description: "过滤匹配项"
  - name: "sort"
    description: "按优先级排序"
  - name: "display"
    description: "格式化输出"

# 质量指标
quality:
  score: 89
  dimensions:
    clarity: 95          # 需求清晰度
    completeness: 85     # 完整性
    feasibility: 92      # 可行性
    testability: 88      # 可测试性

# 下一步
next_step: "design"
recommended_tools:
  - "Bash (Grep)"
  - "Read"
```

**字段说明**:

| Section | Field | Required | Description |
|---------|-------|----------|-------------|
| artifact | version | ✅ | Intent schema版本 |
| artifact | id | ✅ | 唯一标识符 (INT-YYYY-MM-DD-NNN) |
| artifact | type | ✅ | 制品类型 (固定值: intent) |
| metadata | name | ✅ | 组件名称（小写字母+连字符） |
| metadata | description | ✅ | 简短描述（一句话） |
| metadata | component_type | ✅ | 组件类型 (skill/command/agent/hook) |
| metadata | complexity | ❌ | 复杂度 (simple/medium/complex) |
| requirements | functional | ✅ | 功能需求列表 |
| requirements | non_functional | ❌ | 非功能需求（性能/安全/可用性） |
| constraints | hard | ✅ | 硬约束（必须满足） |
| constraints | soft | ❌ | 软约束（建议满足） |
| decisions | - | ✅ | 关键设计决策记录 |
| workflow_pattern | - | ❌ | 工作流模式名称 |
| quality | score | ✅ | 质量评分 (0-100) |

**最小必需字段示例**:

```yaml
version: "3.0"
id: "INT-2026-03-07-001"
type: "intent"

metadata:
  name: "simple-tool"
  description: "A simple tool"
  component_type: "skill"

requirements:
  functional:
    - "核心功能描述"

constraints:
  hard:
    - "必须满足的约束"

decisions:
  - id: "DEC-001"
    decision: "组件类型选择"
    rationale: "原因"
    selected: "Skill"

quality:
  score: 75
```

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
/cmd-init "我想创建一个 Skill 来快速查找项目中的 TODO 注释"
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
Next: Run /cmd-design to generate Blueprint
```

**生成文件**: `docs/ccc/intent/2026-03-07-INT-001.yaml`

### Example 2: 创建复杂的多阶段工具

```bash
/cmd-init "我要做一个自动部署工具，支持 Kubernetes 和 Docker，需要配置验证和回滚功能"
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
Next: Run /cmd-design to generate Blueprint
```

### Example 3: 多语言支持（英文输出）

```bash
/cmd-init "I want to create a code review assistant that checks style and suggests improvements" --lang=en-us
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
Next: Run /cmd-design to generate Blueprint
```

### Example 4: 交互式输入（未提供描述）

```bash
/cmd-init
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
/cmd-init "做个东西"
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

You can run /cmd-init again with a clearer description.
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
Next: Run /cmd-design to generate Blueprint
```
