---
name: requirement-core
description: "需求分析 (Requirement)：澄清技术 +5Why 方法论→挖掘真实需求。原则：问为什么直到根因。触发：需求/想要什么/目标/requirement/clarify"
argument-hint: "<user-requirement> [context-files...]"
context: fork
model: sonnet
allowed-tools:
  - Read
  - Write
---

# 需求分析核心

## Purpose

Requirement 是 CCC 工作流的 Stage 1 需求分析核心组件，负责使用 5Why 方法论深度挖掘用户的真实需求。通过连续追问"为什么"，穿透表面需求找到根本目标，避免解决错误的问题。

## Workflow

### Step 1: 接收原始需求
**目标**: 记录用户初始需求表述
**操作**:
1. 读取用户输入的需求描述
2. 识别关键词和意图
3. 记录上下文文件 (如有)
**输出**: 原始需求记录
**错误处理**: 需求为空时提示输入

### Step 2: 执行 5Why 分析
**目标**: 挖掘需求背后的真实目标
**操作**: 连续追问最多 5 层为什么：

```
Why 1: 为什么需要这个功能？→ 直接原因
Why 2: 为什么这个原因重要？→ 业务价值
Why 3: 为什么当前方案不行？→ 痛点分析
Why 4: 为什么是这个时机？→ 紧迫性评估
Why 5: 为什么是这个方向？→ 战略对齐
```

**输出**: 5Why 分析树
**错误处理**: 用户无法回答时记录已知信息继续

### Step 3: 需求澄清矩阵
**目标**: 多维度澄清需求
**操作**: 从以下维度分析：

| 维度 | 问题 |
|------|------|
| WHO | 谁是最终用户？谁会受到影响？ |
| WHAT | 具体要做什么？交付物是什么？ |
| WHEN | 何时需要？时间窗口？ |
| WHERE | 在哪里使用？集成到哪里？ |
| WHY | 为什么要做？业务价值？ |
| HOW | 如何实现？技术约束？ |

**输出**: 需求澄清矩阵
**错误处理**: 信息不足时标注"待确认"

### Step 4: 需求分类
**目标**: 将需求归类到标准类型
**操作**: 基于需求特征分类：

**功能类型**:
- 新建功能 (Greenfield)
- 功能增强 (Enhancement)
- 问题修复 (Bug Fix)
- 技术债务 (Tech Debt)
- 性能优化 (Optimization)

**复杂度类型**:
- Simple: 单一操作，<5 行代码
- Medium: 多步骤，需要协调
- Complex: 系统性改动，多组件影响

**输出**: 需求分类标签
**错误处理**: 无法明确分类时选择最接近的

### Step 5: 生成需求规格
**目标**: 输出结构化需求文档
**操作**:
1. 整合 5Why 分析结果
2. 整合需求澄清矩阵
3. 添加验收标准
4. 创建 Stage 1 输出文件
**输出**: `docs/designs/{project-name}/stage-1-requirement.md`
**错误处理**: 写入失败时重试并报告

## Input Format

### 基本输入
```
<user-requirement> [context-files...]
```

### 输入示例
```
我想要一个技能来自动查找项目中的 TODO 注释
@docs/requirements.md @src/config.yaml
```

```
需要一个 SubAgent 来处理代码审查流程，包括：
1. 读取变更文件
2. 检查编码规范
3. 生成审查报告

当前我们手动做这个太耗时了
```

### 结构化输入 (可选)
```yaml
requirement:
  statement: "自动查找 TODO 注释"
  context:
    - docs/requirements.md
    - src/config.yaml
  priority: high
  deadline: "2024-03-15"
  stakeholders:
    - "开发团队"
    - "代码审查员"
```

## Output Format

### 标准输出结构
```json
{
  "originalRequirement": "原始需求描述",
  "fiveWhyAnalysis": {
    "why1": {"question": "...", "answer": "..."},
    "why2": {"question": "...", "answer": "..."},
    "why3": {"question": "...", "answer": "..."},
    "rootCause": "根本原因/目标"
  },
  "clarificationMatrix": {
    "who": "...",
    "what": "...",
    "when": "...",
    "where": "...",
    "why": "...",
    "how": "..."
  },
  "classification": {
    "functionType": "新建功能 | 增强 | 修复 | 优化",
    "complexity": "simple|medium|complex",
    "priority": "high|medium|low"
  },
  "acceptanceCriteria": [
    "验收标准 1",
    "验收标准 2"
  ]
}
```

### Markdown 输出示例
```markdown
# 需求规格文档

## 原始需求
> 我想要一个技能来自动查找项目中的 TODO 注释

## 5Why 分析

| 层级 | 问题 | 回答 |
|------|------|------|
| Why 1 | 为什么需要查找 TODO？ | 手动查找太慢 |
| Why 2 | 为什么手动慢有问题？ | 代码审查效率低 |
| Why 3 | 为什么审查效率低？ | TODO 容易被遗漏 |
| Root | 根本目标 | 提高代码审查覆盖率和效率 |

## 需求澄清矩阵

| 维度 | 说明 |
|------|------|
| WHO | 开发团队、代码审查员 |
| WHAT | 自动搜索 TODO 并生成报告 |
| WHEN | 每次代码审查前 |
| WHERE | 项目代码库 |
| WHY | 提高审查效率，避免遗漏 |
| HOW | 使用 Grep 搜索 TODO 模式 |

## 需求分类
- **功能类型**: 效率工具
- **复杂度**: simple
- **优先级**: medium

## 验收标准
1. 能搜索所有代码文件中的 TODO
2. 支持按优先级排序 (@high, @medium, @low)
3. 输出格式清晰可读
```

## Error Handling

| 错误场景 | 处理策略 | 示例 |
|----------|----------|------|
| 需求描述模糊 | 生成澄清问题列表引导用户 | "请说明：1. 搜索范围？2. 输出格式？3. 优先级规则？" |
| 用户跳过 5Why | 基于已有信息推断，标注不确定性 | "假设根本目标是提高效率，如不正确请纠正" |
| 需求自相矛盾 | 指出矛盾点，请求澄清 | "您需要快速响应但又要深度分析，请确定优先级" |
| 上下文文件缺失 | 记录缺失文件，继续分析 | "@docs/missing.md 不存在，继续基于其他信息分析" |
| 需求过于宏大 | 建议拆分为多个子需求 | "这个需求可以拆分为 3 个独立功能，建议分步实施" |
| 输出文件写入失败 | 重试 1 次，仍失败则返回内存结果 | "文件写入失败，结果已保存在内存中" |

## Examples

### Example 1: TODO 查找技能

**输入**:
```
我想要一个技能来自动查找项目中的 TODO 注释
```

**输出**:
```json
{
  "originalRequirement": "自动查找 TODO 注释",
  "fiveWhyAnalysis": {
    "why1": {"question": "为什么需要？", "answer": "手动查找太慢"},
    "why2": {"question": "为什么慢有问题？", "answer": "审查效率低"},
    "why3": {"question": "为什么效率低？", "answer": "TODO 容易遗漏"},
    "rootCause": "提高代码审查覆盖率和效率"
  },
  "classification": {
    "functionType": "效率工具",
    "complexity": "simple"
  }
}
```

### Example 2: 代码审查 SubAgent

**输入**:
```
需要一个 SubAgent 来处理代码审查流程
```

**输出**:
```json
{
  "originalRequirement": "自动化代码审查流程",
  "fiveWhyAnalysis": {
    "why1": {"question": "为什么需要？", "answer": "手动审查耗时"},
    "why2": {"question": "为什么耗时是问题？", "answer": "延迟发布周期"},
    "why3": {"question": "为什么延迟发布？", "answer": "审查是瓶颈"},
    "rootCause": "缩短发布周期，提高交付速度"
  },
  "classification": {
    "functionType": "流程自动化",
    "complexity": "complex"
  }
}
```

### Example 3: 性能优化需求

**输入**:
```
系统响应太慢，需要优化查询性能
```

**输出**:
```json
{
  "originalRequirement": "优化查询性能",
  "fiveWhyAnalysis": {
    "why1": {"question": "为什么需要优化？", "answer": "用户抱怨慢"},
    "why2": {"question": "为什么用户抱怨？", "answer": "超过 3 秒等待"},
    "why3": {"question": "为什么这么慢？", "answer": "缺少索引"},
    "rootCause": "数据库查询缺少索引导致性能低下"
  },
  "classification": {
    "functionType": "性能优化",
    "complexity": "medium"
  }
}
```

### Example 4: 数据迁移需求

**输入**:
```
需要将用户数据从旧系统迁移到新系统
```

**输出**:
```json
{
  "originalRequirement": "用户数据迁移",
  "fiveWhyAnalysis": {
    "why1": {"question": "为什么迁移？", "answer": "旧系统退役"},
    "why2": {"question": "为什么退役？", "answer": "维护成本高"},
    "why3": {"question": "为什么成本高？", "answer": "技术过时"},
    "rootCause": "降低维护成本，现代化技术栈"
  },
  "classification": {
    "functionType": "数据迁移",
    "complexity": "complex"
  }
}
```

### Example 5: 文档生成需求

**输入**:
```
想要自动生成 API 文档
```

**输出**:
```json
{
  "originalRequirement": "自动生成 API 文档",
  "fiveWhyAnalysis": {
    "why1": {"question": "为什么需要？", "answer": "手动更新太麻烦"},
    "why2": {"question": "为什么麻烦？", "answer": "容易忘记更新"},
    "why3": {"question": "为什么忘记？", "answer": "没有自动化流程"},
    "rootCause": "确保文档与代码同步，提高文档质量"
  },
  "classification": {
    "functionType": "文档自动化",
    "complexity": "medium"
  }
}
```

## Notes

### Best Practices

1. **问到底**: 至少追问 3 层 Why，直到找到根本原因
2. **记录假设**: 用户无法回答时，明确记录假设
3. **多维澄清**: 使用 5W1H 矩阵确保全面理解
4. **验收标准**: 每个需求必须有可验证的验收标准
5. **适度拆分**: 过大需求拆分为可管理的子需求

### Common Pitfalls

1. ❌ **浅层分析**: 只问 1-2 个 Why 就停止
2. ❌ **过度假设**: 不做假设或做太多假设
3. ❌ **忽略约束**: 不考虑时间、资源约束
4. ❌ **模糊验收**: 验收标准不可测量
5. ❌ **需求膨胀**: 一个需求包含太多功能

### 5Why Methodology

```
表面需求 → 直接原因 → 业务价值 → 痛点分析 → 根本目标

示例:
"需要查找 TODO"
  → Why? "手动太慢"
  → Why? "审查效率低"
  → Why? "TODO 容易遗漏"
  → Why? "没有自动化"
  → Root: "需要自动化提高审查覆盖率"
```

### Integration with CCC Workflow

```
用户输入
    ↓
Requirement (本组件) → 5Why 分析 + 需求澄清
    ↓
Stage 1 Output (需求规格)
    ↓
Advisor (架构推荐) → Stage 1 推荐
    ↓
Architect (架构选型) → Stage 2
    ↓
Design (详细设计) → Stage 3
    ↓
Validator (规范验证) → Stage 4
    ↓
Planner (实施规划) → Stage 5
```

### File References

- 输出文件：`docs/designs/{project-name}/stage-1-requirement.md`
- 参考模板：`docs/templates/requirement-template.md`
- 方法论：`docs/methods/5why-analysis.md`
