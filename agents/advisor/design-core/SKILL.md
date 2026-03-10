---
name: design-core
description: "阶段 3 详细设计核心：基于架构决策创建 YAML 配置、工作流步骤和工具权限。触发：设计/详细/配置/workflow"
argument-hint: "<stage-2-output-path>"
context: fork
model: sonnet
allowed-tools:
  - Read
  - Write
skills:
  - ccc:std-component-selection
  - ccc:lib-design-patterns
---

# Design Core (Stage 3)

## Purpose

Design Core 是 CCC 工作流的阶段 3 组件，负责基于阶段 2 架构决策创建详细设计规格。本组件将高层架构转化为具体的 YAML 配置、详细工作流步骤和最小权限工具声明。

## Workflow

### Step 1: 读取阶段 2 输出
**目标**: 加载阶段 2 的架构决策
**操作**:
1. 读取 stage-2-architecture.md 文件
2. 解析组件类型决策 (Skill/SubAgent)
3. 提取推荐的设计模式
4. 识别约束条件和需求
**输出**: 架构决策摘要
**错误处理**: 如果阶段 2 输出缺失，请求先完成架构阶段

### Step 2: 设计 YAML 配置
**目标**: 创建组件的 YAML frontmatter
**操作**:
1. 从组件用途生成 kebab-case 名称
2. 编写 50-200 字符描述，包含触发词
3. 基于决策树确定上下文 (参考 Context Selection Guide)
4. 基于决策矩阵选择模型 (参考 Model Selection Guide)
5. 定义最小必要工具集
6. 验证 skill 加载策略 (command 避免显式加载 3+ skill)
**输出**: 完整 YAML frontmatter
**错误处理**: 如果配置无效，提供正确语法的模板

### Step 3: 设计工作流步骤
**目标**: 创建详细的逐步工作流
**操作**:
1. 将功能分解为离散步骤
2. 对每个步骤定义：
   - 目标 (实现什么)
   - 操作 (具体行动)
   - 输出 (产生的结果)
   - 错误处理 (失败响应)
3. 确保每个步骤单一职责
4. 验证步骤间的逻辑流
**输出**: 包含 4-8 步的完整工作流
**错误处理**: 如果工作流不完整，识别差距并建议缺失步骤

### Step 3.5: 生成证据链
**目标**: 建立从需求到skill的完整追溯链
**操作**:
1. 创建能力需求表：工作流步骤 → 所需能力 → 输入输出
2. 创建Skill映射表：能力 → Skill名称 → 状态（现有/迭代/新建）
3. 对每个skill说明：
   - 为什么选择这个skill
   - 如果是迭代/新建，说明原因
4. 生成验证清单
**输出**: 完整证据链文档（参考 docs/evidence-chain-specification.md）
**错误处理**: 如果skill引用不存在，标记为"新建"并说明需要创建的原因

### Step 4: 定义输入/输出格式
**目标**: 指定接口契约
**操作**:
1. 定义基本输入语法
2. 创建输入示例 (基本和结构化)
3. 定义输出 JSON 结构
4. 创建 Markdown 输出示例
**输出**: 完整 I/O 规范
**错误处理**: 如果格式不明确，使用标准模板

### Step 5: 创建错误处理文档
**目标**: 文档化失败场景和响应
**操作**:
1. 从工作流步骤识别潜在失败点
2. 对每个失败定义：
   - 错误场景
   - 处理策略
   - 示例错误消息
3. 格式化为标准表格
**输出**: 错误处理表格
**错误处理**: 如果特定场景不明确，使用通用模式

### Step 6: 生成示例和注释
**目标**: 添加使用示例和最佳实践
**操作**:
1. 创建 5 个多样化示例，覆盖：
   - 基本用法
   - 带选项的高级用法
   - 错误场景处理
   - 集成模式
   - 边界情况
2. 生成注释章节，包含：
   - 最佳实践 (5+ 项)
   - 常见陷阱 (5+ 项)
   - 相关表格和指南
**输出**: 完整示例和注释章节
**错误处理**: 如果生成失败，使用模板示例

### Step 7: 写入输出文件
**目标**: 保存设计规格到文件
**操作**:
1. 创建目录：`docs/designs/{project-name}/`
2. 写入完整设计到：`stage-3-detailed-design.md`
3. 验证文件写入成功
**输出**: 文件路径确认
**错误处理**: 使用备选路径重试，如果持续失败则报告错误

## Input Format

### Basic Input
```
<stage-2-output-path>
```

### Input Examples
```
docs/designs/my-project/stage-2-architecture.md
```

```
docs/designs/api-gateway/stage-2-architecture.md
```

### Structured Input (Optional)
```yaml
task: create-detailed-design
stage_2_path: docs/designs/my-project/stage-2-architecture.md
options:
  include_diagrams: true
  min_steps: 4
  max_steps: 8
```

## Output Format

### Standard Output Structure
```json
{
  "status": "completed",
  "stage": 3,
  "design": {
    "yaml_config": {
      "name": "data-processor",
      "context": "fork",
      "model": "sonnet",
      "allowed_tools": ["Read", "Write", "Bash", "Task"]
    },
    "workflow_steps": 5,
    "execution_phases": 2
  },
  "output_path": "docs/designs/my-project/stage-3-detailed-design.md",
  "validation": {
    "yaml_valid": true,
    "workflow_complete": true,
    "tools_minimal": true
  }
}
```

### Markdown Output Example
```markdown
# 设计规格文档

## YAML 配置
```yaml
---
name: data-processor
description: "处理数据文件，包含验证和转换"
context: fork
model: sonnet
allowed-tools:
  - Read
  - Write
  - Bash
  - Task
---
```

## 工作流设计

### Step 1: 验证输入
**目标**: 验证输入文件格式
**操作**: 读取并检查文件结构
**输出**: 验证结果
**错误处理**: 格式错误时返回带行号的错误

### Step 2: 转换数据
**目标**: 将数据转换为目标格式
**操作**: 应用转换规则
**输出**: 转换后的数据
**错误处理**: 失败时保留原始数据

## 证据链

### 能力需求表

| 阶段 | 需要的能力 | 能力说明 | 输入 | 输出 |
|------|-----------|---------|------|------|
| 验证输入 | 文件读取与解析 | 读取文件并验证JSON/YAML格式 | 文件路径 | 验证结果 |
| 转换数据 | 数据转换 | 应用转换规则生成目标格式 | 验证后的数据 | 转换后的数据 |

### Skill映射表

| 能力 | Skill名称 | 状态 | 说明 |
|------|----------|------|------|
| 文件读取与解析 | Read工具 | 现有 | 使用内置Read工具读取文件 |
| 数据转换 | 无需skill | - | 在主逻辑中实现转换规则 |

### 验证清单

- [x] 每个工作流步骤都有明确的输入输出
- [x] 所有能力都有对应的工具或实现方案
- [x] 数据流转路径完整：文件路径→验证结果→转换后的数据

## 执行阶段

| 阶段 | 名称 | 人机交互 | 触发方式 | 上下文 |
|------|------|----------|----------|--------|
| 1 | process | 无 | 自动 | fork |
| 2 | report | 无 | 自动 | fork |
```

## Error Handling

| 错误场景 | 处理策略 | 示例 |
|----------|----------|------|
| 缺少架构决策 | 请求先完成阶段 2 架构 | "请先完成阶段 2 架构" |
| YAML 配置无效 | 提供正确语法的模板 | "无效的 YAML：第 5 行缺少冒号" |
| 工具权限过多 | 建议最小必要工具集 | "只读操作不需要 Write" |
| 工作流步骤不完整 | 识别差距并建议缺失步骤 | "缺少错误处理步骤" |
| 文件输出失败 | 使用备选路径重试，持续失败则报告错误 | "写入失败，重试中..." |

## Examples

### Example 1: 简单只读技能设计

**Input**:
```
docs/designs/lookup/stage-2-architecture.md
```

**Output**:
```json
{
  "status": "completed",
  "design": {
    "yaml_config": {
      "name": "doc-lookup",
      "context": "main",
      "model": "haiku",
      "allowed_tools": ["Read", "Grep"]
    },
    "workflow_steps": 2
  }
}
```

### Example 2: 多步骤 SubAgent 设计

**Input**:
```
docs/designs/processor/stage-2-architecture.md
```

**Output**:
```json
{
  "status": "completed",
  "design": {
    "yaml_config": {
      "name": "data-processor",
      "context": "fork",
      "model": "sonnet",
      "allowed_tools": ["Read", "Write", "Bash", "Task"]
    },
    "workflow_steps": 5
  }
}
```

### Example 3: 带并行执行的设计

**Input**:
```
docs/designs/reviewer/stage-2-architecture.md
```

**Output**:
```json
{
  "status": "completed",
  "design": {
    "execution_phases": 2,
    "parallel_components": ["review-core", "architecture-analyzer"]
  }
}
```

### Example 4: 带用户交互的设计

**Input**:
```
docs/designs/advisor/stage-2-architecture.md
```

**Output**:
```json
{
  "status": "completed",
  "design": {
    "execution_phases": 3,
    "user_interaction_phase": 2
  }
}
```

### Example 5: 设计验证失败

**Input**:
```
docs/designs/incomplete/stage-2-architecture.md
```

**Output**:
```json
{
  "status": "warning",
  "warnings": [
    {"type": "MISSING_ERROR_HANDLING", "message": "工作流缺少错误处理步骤"},
    {"type": "EXCESSIVE_TOOLS", "message": "声明的工具超过需求：Bash, Glob"}
  ]
}
```

## Notes

### Best Practices

1. **最小权限**: 只声明实际需要的工具
2. **清晰步骤**: 每个步骤应该有单一职责
3. **错误处理**: 工作流中始终包含错误处理
4. **上下文优先级**: 人机交互 → main，多步骤复杂任务 → fork
5. **模型多维评估**: 综合任务复杂度、推理深度、上下文大小选择模型
6. **Skill 加载策略**: Command 避免显式加载 3+ skill，考虑拆分或改为 subagent

### Common Pitfalls

1. ❌ **过度声明**: 声明超过需要的工具"以防万一"
2. ❌ **模糊步骤**: 如"do magic"没有清晰操作
3. ❌ **缺少错误**: 工作流中没有错误处理
4. ❌ **忽略人机交互**: 需要用户交互的 command 使用 fork 导致无法访问主会话
5. ❌ **Skill 过载**: Command 显式加载 3+ skill 增加上下文消耗
6. ❌ **单维度模型选择**: 只看任务类型，忽略推理深度和上下文大小

### Design Principles

| 原则 | 描述 | 示例 |
|------|------|------|
| 单一职责 | 每个步骤做一件事 | "解析输入" 而不是 "解析和验证和转换" |
| 显式错误处理 | 文档化错误如何处理 | "返回带行号的错误消息" |
| 最小权限 | 只必要的工具 | 只读任务不需要 Write |
| 清晰 I/O | 为每个步骤定义输入输出 | "输入：文件路径，输出：解析内容" |

### Context Selection Guide

**决策树（按优先级）：**

1. **人机交互需求** → main
   - 需要用户确认、选择、输入
   - 需要访问主会话历史
   - 示例：advisor-core 的用户确认阶段

2. **Skill 数量** → 评估设计
   - Command 显式加载 3+ skill → 设计错误信号，考虑拆分或改为 subagent
   - Command 应依赖隐式发现，subagent 使用初始加载

3. **任务复杂度** → fork/main
   - 多步骤 + 使用 Write/Task → fork
   - 简单、单步骤、只读 → main

**快速参考表：**

| 场景 | 上下文 | 原因 |
|------|--------|------|
| 需要用户交互 | main | 访问主会话历史 |
| Command 加载 3+ skill | 重新设计 | 上下文消耗过大 |
| 多步骤 + Write/Task | fork | 隔离执行环境 |
| 简单只读查询 | main | 无需隔离 |

### Model Selection Guide

**决策矩阵（多维度评估）：**

| 维度 | haiku | sonnet | opus |
|------|-------|--------|------|
| 任务复杂度 | 简单查找、格式转换 | 标准工作流、分析 | 复杂推理、架构决策 |
| 推理深度 | 1-2 层 | 3-5 层 | 6+ 层 |
| 上下文大小 | < 10K tokens | 10K-50K tokens | > 50K tokens |
| 输出质量要求 | 格式化输出 | 结构化分析 | 创造性设计 |

**选择流程：**

1. 评估任务复杂度（主要维度）
2. 检查推理深度需求
3. 估算上下文大小
4. 综合判断，优先满足复杂度要求

**示例：**
- 读取文件返回内容 → haiku（简单+浅推理+小上下文）
- 代码审查生成报告 → sonnet（标准+中推理+中上下文）
- 架构决策与权衡分析 → opus（复杂+深推理+大上下文）

### Integration with CCC Workflow

```
阶段 2：架构决策
    ↓
Design Core (本组件) → 设计规格
    ↓
阶段 4：验证 → 验证设计
```

### File References

- 输入：`docs/designs/{project}/stage-2-architecture.md`
- 输出：`docs/designs/{project}/stage-3-detailed-design.md`