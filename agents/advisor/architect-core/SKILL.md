---
name: architect-core
description: "架构选型 (Architect)：基于需求选择组件类型→匹配架构设计模式。触发：架构/组件类型/设计模式/architect/选型"
argument-hint: "<stage-1-output-path>"
context: fork
model: sonnet
allowed-tools:
  - Read
  - Write
skills:
  - ccc:std-component-selection
  - ccc:lib-design-patterns
---

# 架构选型核心

## Purpose

Architect 是 CCC 工作流的 Stage 2 核心组件，负责基于 Stage 1 的需求分析结果，选择合适的组件类型并匹配相应的架构设计模式。本组件将抽象需求转化为具体的架构决策，为后续详细设计奠定基础。

## Workflow

### Step 1: 读取 Stage 1 输出
**目标**: 加载需求分析结果
**操作**:
1. 读取 `docs/designs/{project-name}/stage-1-requirement.md`
2. 解析架构推荐和诊断结果
3. 提取约束条件和复杂度信息
**输出**: 结构化的需求数据
**错误处理**: 文件不存在时提示先执行 Stage 1

### Step 2: 确定组件类型
**目标**: 选择 Skill 或 SubAgent 类型
**操作**: 基于以下维度决策：
- 是否需要调用其他 agent → SubAgent
- 是否多步骤工作流 → SubAgent
- 是否只读单步骤 → Skill
- 是否需要写入 → Skill (fork context) 或 SubAgent
**输出**: 组件类型决策
**错误处理**: 模糊情况下提供 2 个备选方案

### Step 3: 选择设计模式
**目标**: 匹配最适合的架构设计模式
**操作**: 根据组件类型和需求特征选择：

**Skill 模式库**:
- Search-Filter-Sort: 搜索过滤场景
- Transform-Validate: 数据转换场景
- Read-Compute-Write: 计算处理场景

**SubAgent 模式库**:
- Pipeline-Processor: 多步骤流水线
- Recursive-Analyzer: 递归分析场景
- Interactive-Wizard: 交互式引导
- Coordinator-Dispatcher: 任务协调分发
**输出**: 设计模式选择
**错误处理**: 无匹配模式时建议自定义模式

### Step 4: 规划工具集合
**目标**: 确定最小必要工具权限
**操作**:
1. 分析工作流步骤需要的操作
2. 选择最小工具集合
3. 验证工具组合的充分性
**输出**: 工具权限列表
**错误处理**: 工具过多时提示精简，过少时提示补充

### Step 5: 选择执行模型
**目标**: 匹配合适的 Claude 模型
**操作**: 基于复杂度选择：
- simple → haiku (快速响应)
- medium → sonnet (平衡性能)
- complex → opus (深度推理)
**输出**: 模型选择决策
**错误处理**: 模型不可用时降级到次选

### Step 6: 输出架构决策
**目标**: 生成 Stage 2 架构规格
**操作**:
1. 创建 `docs/designs/{project-name}/stage-2-architecture.md`
2. 写入架构决策和理由
3. 验证文件写入成功
**输出**: Stage 2 输出文件路径
**错误处理**: 写入失败时重试并报告

## Input Format

### 输入路径
```
<stage-1-output-path>
```

### Stage 1 输入示例
```markdown
# 架构推荐报告

## 诊断结果
| 维度 | 答案 |
|------|------|
| 组件类型 | Skill |
| 数据流 | 输入：文件路径，输出：TODO 列表 |
| 复杂度 | 简单 |
| 约束 | 只读、多文件支持 |

## 推荐配置
```yaml
---
name: todo-finder
context: main
model: haiku
allowed-tools:
  - Read
  - Grep
---
```
```

### JSON 输入示例 (可选)
```json
{
  "diagnosis": {
    "componentType": "SubAgent",
    "complexity": "complex",
    "constraints": ["需要写权限", "多步骤工作流"]
  },
  "recommendation": {
    "pattern": "Pipeline-Processor"
  }
}
```

## Output Format

### 标准输出结构
```json
{
  "architectureDecision": {
    "componentType": "Skill|SubAgent",
    "designPattern": "模式名称",
    "context": "main|fork",
    "model": "haiku|sonnet|opus",
    "allowedTools": ["工具列表"]
  },
  "reasoning": {
    "componentTypeReason": "选择组件类型的理由",
    "patternReason": "选择设计模式的理由",
    "modelReason": "选择模型的理由"
  },
  "fileReferences": [
    {
      "path": "文件路径",
      "purpose": "用途说明"
    }
  ]
}
```

### Markdown 输出示例
```markdown
# 架构决策文档

## 组件类型
**决策**: SubAgent
**理由**: 需要调用多个子任务，涉及多步骤工作流

## 设计模式
**决策**: Pipeline-Processor
**理由**: 数据处理流程清晰，各步骤独立可测

## 执行上下文
**决策**: fork
**理由**: 需要写入输出文件，隔离执行环境

## 模型选择
**决策**: sonnet
**理由**: 中等复杂度，需要平衡响应速度和质量

## 工具权限
```yaml
allowed-tools:
  - Read      # 读取输入文件
  - Write     # 写入输出文件
  - Bash      # 执行处理脚本
  - Task      # 调用子任务
```

## 文件引用
- @docs/designs/{project}/stage-1-requirement.md - 需求输入
- @src/pipeline/ - 处理逻辑目录
```

## Error Handling

| 错误场景 | 处理策略 | 示例 |
|----------|----------|------|
| Stage 1 文件不存在 | 提示先执行 Advisor (Stage 1) | "请先运行 advisor-core 生成 stage-1-requirement.md" |
| 需求信息不完整 | 基于已有信息做合理推断，标注假设 | "假设复杂度为 medium，使用 sonnet 模型" |
| 设计模式不匹配 | 提供最近的替代模式或建议自定义 | "无精确匹配，建议使用 Pipeline-Processor 变体" |
| 工具权限冲突 | 识别冲突并提供解决方案 | "Read 和 Write 需要 fork context，不能与 main 共用" |
| 模型选择超出预算 | 提供降级方案 | "opus 成本较高，sonnet 可处理 80% 场景" |
| 输出文件写入失败 | 重试 1 次，仍失败则返回内存结果 | "文件写入失败，结果已保存在内存中" |

## Examples

### Example 1: 简单查询 Skill

**输入**: Stage 1 推荐 TODO 查找技能

**输出**:
```json
{
  "architectureDecision": {
    "componentType": "Skill",
    "designPattern": "Search-Filter-Sort",
    "context": "main",
    "model": "haiku",
    "allowedTools": ["Read", "Grep"]
  },
  "reasoning": {
    "componentTypeReason": "单步骤只读查询，无需 SubAgent",
    "patternReason": "典型的搜索 - 过滤 - 排序场景",
    "modelReason": "简单逻辑，haiku 足够处理"
  }
}
```

### Example 2: 代码审查 SubAgent

**输入**: Stage 1 推荐代码审查 SubAgent

**输出**:
```json
{
  "architectureDecision": {
    "componentType": "SubAgent",
    "designPattern": "Pipeline-Processor",
    "context": "fork",
    "model": "sonnet",
    "allowedTools": ["Read", "Write", "Bash", "Task"]
  },
  "reasoning": {
    "componentTypeReason": "多步骤工作流，需要 Task 协调",
    "patternReason": "审查流程为典型流水线：读取→检查→报告",
    "modelReason": "中等复杂度，需要理解代码语义"
  }
}
```

### Example 3: 数据分析 SubAgent

**输入**: Stage 1 推荐数据分析 SubAgent

**输出**:
```json
{
  "architectureDecision": {
    "componentType": "SubAgent",
    "designPattern": "Recursive-Analyzer",
    "context": "fork",
    "model": "opus",
    "allowedTools": ["Read", "Glob", "Grep", "Task"]
  },
  "reasoning": {
    "componentTypeReason": "需要递归分析大量数据",
    "patternReason": "递归模式适合树状数据结构分析",
    "modelReason": "复杂分析需要 opus 的深度推理"
  }
}
```

### Example 4: 配置转换 Skill

**输入**: Stage 1 推荐 YAML 到 JSON 转换技能

**输出**:
```json
{
  "architectureDecision": {
    "componentType": "Skill",
    "designPattern": "Transform-Validate",
    "context": "fork",
    "model": "sonnet",
    "allowedTools": ["Read", "Write", "Bash"]
  },
  "reasoning": {
    "componentTypeReason": "单步骤转换，无需 SubAgent",
    "patternReason": "典型的转换 + 验证模式",
    "modelReason": "需要理解 YAML/JSON 结构，sonnet 适合"
  }
}
```

### Example 5: 交互式向导 SubAgent

**输入**: Stage 1 推荐配置生成向导

**输出**:
```json
{
  "architectureDecision": {
    "componentType": "SubAgent",
    "designPattern": "Interactive-Wizard",
    "context": "fork",
    "model": "sonnet",
    "allowedTools": ["Read", "Write"]
  },
  "reasoning": {
    "componentTypeReason": "需要多轮对话交互",
    "patternReason": "向导模式适合逐步引导用户",
    "modelReason": "需要理解用户意图，sonnet 平衡速度和智能"
  }
}
```

## Notes

### Best Practices

1. **遵循 Stage 1 推荐**: 除非有明显错误，否则遵循 Advisor 的推荐
2. **最小权限原则**: 工具权限只包括必需的，不包括可能用到的
3. **模式优先**: 优先选择已知设计模式，减少自定义
4. **文档化理由**: 每个决策都要有清晰的理由说明
5. **向前兼容**: 考虑未来可能的扩展需求

### Common Pitfalls

1. ❌ **过度设计**: 简单需求选择复杂架构
2. ❌ **权限膨胀**: 包含不必要的工具权限
3. ❌ **模式误用**: 强行套用不匹配的设计模式
4. ❌ **忽略约束**: 不考虑 Stage 1 提出的约束条件
5. ❌ **缺少理由**: 决策没有说明为什么

### Design Pattern Library

#### Skill Patterns
| 模式 | 用途 | 典型工具 |
|------|------|----------|
| Search-Filter-Sort | 搜索过滤 | Read, Grep |
| Transform-Validate | 数据转换 | Read, Write, Bash |
| Read-Compute-Write | 计算处理 | Read, Write |

#### SubAgent Patterns
| 模式 | 用途 | 典型工具 |
|------|------|----------|
| Pipeline-Processor | 多步骤流水线 | Read, Write, Task |
| Recursive-Analyzer | 递归分析 | Read, Glob, Task |
| Interactive-Wizard | 交互引导 | Read, Write |
| Coordinator-Dispatcher | 任务协调 | Task, Read, Write |

### Integration with CCC Workflow

```
Stage 1 (Advisor) → 架构推荐
    ↓
Stage 2 (Architect - 本组件) → 架构决策
    ↓
Stage 3 (Design) → 详细设计
    ↓
Stage 4 (Validator) → 规范验证
    ↓
Stage 5 (Planner) → 实施规划
```

### File References

- 输入文件：`docs/designs/{project-name}/stage-1-requirement.md`
- 输出文件：`docs/designs/{project-name}/stage-2-architecture.md`
- 模式库：`docs/architecture/patterns-library.md`
