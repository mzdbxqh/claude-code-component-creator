---
name: cmd-design
model: sonnet
context: fork
disable-model-invocation: true
allowed-tools: [Read, Write, Edit, Glob, Grep]
description: "5阶段设计流程生成Blueprint。触发：设计/创建方案。从Intent创建详细设计。主工作流第2步。"
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

## 资源预算

### Token 使用估计

| 场景 | 输入 Token | 输出 Token | 总计 | 说明 |
|------|-----------|-----------|------|------|
| 小型组件 | 8K-15K | 5K-10K | 13K-25K | 单一职责 Skill |
| 中型组件 | 15K-30K | 10K-20K | 25K-50K | 多步骤工作流 Subagent |
| 大型组件 | 30K-60K | 20K-40K | 50K-100K | 复杂编排 Command |

### Token 使用分解

**阶段 1: Intent 读取** (2K-5K tokens)
- 读取 Intent 制品文件
- 解析需求和约束
- 提取用户意图

**阶段 2: SubAgent 调用** (15K-40K tokens)
- ccc:advisor-core: 3K-8K (4个诊断问题 + 架构推荐)
- ccc:requirement-core: 4K-10K (需求澄清 + 结构化)
- ccc:architect-core: 5K-12K (工作流设计 + 组件结构)
- ccc:blueprint-core: 3K-10K (Blueprint 生成 + 验证)

**阶段 3: 知识库加载** (3K-8K tokens)
- 设计模式库 (lib-design-patterns)
- 架构决策模板
- 参考实现示例

**阶段 4: 输出生成** (5K-15K tokens)
- Blueprint YAML 制品
- 设计决策文档
- 架构图和流程图

### 成本估计

基于 Claude Sonnet 4.5 定价（输入: $3/MTok, 输出: $15/MTok）：

| 场景 | 输入成本 | 输出成本 | 总成本 | 说明 |
|------|----------|----------|--------|------|
| 小型组件 | $0.024-$0.045 | $0.075-$0.150 | $0.10-$0.20 | 适合快速原型 |
| 中型组件 | $0.045-$0.090 | $0.150-$0.300 | $0.20-$0.40 | 标准开发场景 |
| 大型组件 | $0.090-$0.180 | $0.300-$0.600 | $0.40-$0.80 | 复杂系统设计 |

**批量设计成本**:
- 10个小型组件: $1.00-$2.00
- 10个中型组件: $2.00-$4.00
- 5个大型组件: $2.00-$4.00

### 优化建议

**1. 减少上下文加载**
- 仅加载相关的设计模式（避免加载全部库）
- 精简 Intent 内容（移除冗余说明）
- 使用 `--minimal` 模式跳过非必要分析

**2. 批量设计复用**
- 同时设计多个相似组件
- 复用架构决策和设计模式
- 共享 SubAgent 的分析结果

**3. 分层设计策略**
- 先设计核心组件（高复杂度）
- 再设计辅助组件（低复杂度）
- 复用已有组件的设计决策

**4. 渐进式设计**
- 第一轮：快速设计（仅关键部分）
- 第二轮：补充细节（按需迭代）
- 避免一次性设计所有细节

### Token 使用监控

在执行过程中，系统会输出 Token 使用情况：

```
[INFO] Design started for: api-service
[INFO] Token usage: advisor-core (3,245 tokens)
[INFO] Token usage: requirement-core (5,123 tokens)
[INFO] Token usage: architect-core (7,456 tokens)
[INFO] Token usage: blueprint-core (4,321 tokens)
[INFO] Total tokens used: 20,145 (estimated cost: $0.35)
```

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
