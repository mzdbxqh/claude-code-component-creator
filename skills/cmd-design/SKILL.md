---
name: ccc:cmd-design
model: sonnet
context: fork
allowed-tools: [Read, Write, Edit, Glob, Grep]
description: "生成 Blueprint 制品，使用 5 阶段设计流程（需求分析→架构选型→详细设计→验证→规划）。适用场景：从 Intent 创建详细设计方案。输出包含工作流步骤、工具选择、证据链和设计文档的 Blueprint YAML 制品。关键动作：设计、选型、定义、验证。主工作流的第2步。 [支持平台: macOS, Linux, Windows (via WSL)]"
argument-hint: "--name=<name> [--intent-id=current] [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:design

**完整流程**: `init` → **design** → `review` → `fix` → `validate` → `build`

Creates comprehensive blueprint artifacts from intent specifications using structured 5-stage design workflow analysis.

## 模型要求

- **推荐**: Claude Sonnet 4.5+ (高效能,最佳性价比)
- **可用**: Claude Opus 4.5+ (最高质量,复杂设计)
- **最小**: Claude Sonnet 4.5+ (最低要求)

### 功能需求
- 需要支持 Tool Use (Read, Write, Edit, Glob, Grep)
- 需要支持多轮对话和复杂推理
- 建议上下文窗口 >= 200K tokens (处理完整 Intent 和设计模式)

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

## SubAgents 协作

本工作流使用以下 SubAgents 进行任务分解和并行执行：

### 核心 Agents
- **ccc:advisor-core**: 设计顾问，执行 4 个诊断问题，基于决策树推荐架构方案
- **ccc:requirement-core**: 需求分析器，从 Intent 提取和结构化需求
- **ccc:architect-core**: 架构设计器，设计组件结构和工作流
- **ccc:blueprint-core**: Blueprint 生成器，创建最终的 Blueprint 制品

### 调度策略
- **串行执行**: cmd-design → ccc:advisor-core → ccc:requirement-core → ccc:architect-core → ccc:blueprint-core
- **并行执行**: 无（按顺序依赖）
- **错误处理**: 任何 agent 失败时终止工作流并提示用户

### Agent 输入输出
| Agent | 输入 | 输出 |
|-------|------|------|
| ccc:advisor-core | Intent 制品 | 架构推荐方案 |
| ccc:requirement-core | Intent 制品 + 架构方案 | 结构化需求文档 |
| ccc:architect-core | 需求文档 | 组件设计和工作流定义 |
| ccc:blueprint-core | 组件设计 | Blueprint YAML 制品 |

### 调用示例
```
用户: /ccc:design --name=deploy-skill
  ↓
cmd-design 读取 Intent 制品
  ↓
调用 ccc:advisor-core (诊断组件类型、数据流、复杂度、约束)
  ↓
调用 ccc:requirement-core (提取功能和非功能需求)
  ↓
调用 ccc:architect-core (设计工作流和组件结构)
  ↓
调用 ccc:blueprint-core (生成 Blueprint YAML)
  ↓
cmd-design 输出设计文档和 Blueprint 制品
```

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
