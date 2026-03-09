---
name: design-core
description: "阶段 3 详细设计核心：基于架构决策创建 YAML 配置、工作流步骤和工具权限。触发：设计/详细/配置/workflow"
argument-hint: "<stage-2-output-path>"
context: fork
model: sonnet
allowed-tools:
  - Read
  - Write
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
3. 基于复杂度确定上下文 (main/fork)
4. 基于任务类型选择模型 (haiku/sonnet/opus)
5. 定义最小必要工具集
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
4. **上下文选择**: 复杂工作流使用 fork，简单使用 main
5. **模型匹配**: 模型复杂度与任务复杂度匹配

### Common Pitfalls

1. ❌ **过度声明**: 声明超过需要的工具"以防万一"
2. ❌ **模糊步骤**: 如"do magic"没有清晰操作
3. ❌ **缺少错误**: 工作流中没有错误处理
4. ❌ **错误上下文**: 复杂多步骤工作流使用 main
5. ❌ **缺少输出规范**: 没有定义步骤产生什么

### Design Principles

| 原则 | 描述 | 示例 |
|------|------|------|
| 单一职责 | 每个步骤做一件事 | "解析输入" 而不是 "解析和验证和转换" |
| 显式错误处理 | 文档化错误如何处理 | "返回带行号的错误消息" |
| 最小权限 | 只必要的工具 | 只读任务不需要 Write |
| 清晰 I/O | 为每个步骤定义输入输出 | "输入：文件路径，输出：解析内容" |

### Context Selection Guide

| 上下文 | 何时使用 | 示例 |
|--------|----------|------|
| main | 简单、单步骤、只读 | 文件查找、内容显示 |
| fork | 多步骤、使用 Write、Task 调用 | 数据处理、文件生成 |

### Model Selection Guide

| 模型 | 何时使用 | 示例 |
|------|----------|------|
| haiku | 简单查找、格式转换 | 读取文件，返回内容 |
| sonnet | 标准工作流、分析 | 大多数 SubAgents |
| opus | 复杂推理、架构 | 设计决策、验证 |

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