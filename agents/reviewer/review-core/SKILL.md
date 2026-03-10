---
name: review-core
description: "智能审阅核心：基于组件类型加载反模式库→执行深度质量检查→返回结构化结果。触发：审查/检查/review-core/智能审阅"
context: fork
model: haiku
allowed-tools:
  - Read
  - Grep
  - Glob
skills:
  - ccc:std-component-selection
  - ccc:std-naming-rules
  - ccc:lib-antipatterns
---

# Review Core

## Purpose

Review Core 是智能审阅系统的核心检测引擎，负责基于组件类型动态加载对应的反模式库，执行深度质量检查，并返回结构化的审阅结果。与 Reviewer Core 相比，本组件增加了组件类型识别和智能规则匹配能力。

## Workflow

### Step 1: 解析审阅请求
**目标**: 识别审阅目标和组件类型
**操作**:
1. 读取目标文件路径
2. 分析文件内容确定组件类型 (Skill/SubAgent)
3. 提取组件元数据 (name, context, model, tools)
**输出**: 审阅上下文信息
**错误处理**: 无法识别类型时使用启发式规则

### Step 2: 智能加载反模式库
**目标**: 根据组件类型加载最匹配的反模式规则
**操作**:
```
CASE 组件类型 OF
  Skill:
    加载 docs/antipatterns/skill-antipatterns.md
    加载 docs/antipatterns/common-antipatterns.md
  SubAgent:
    加载 docs/antipatterns/subagent-antipatterns.md
    加载 docs/antipatterns/common-antipatterns.md
  Unknown:
    加载 docs/antipatterns/generic-antipatterns.md
END CASE
```
**输出**: 反模式规则集合
**错误处理**: 反模式库缺失时记录警告继续

### Step 3: 多维度质量检查
**目标**: 从多个维度执行深度检查
**操作**:

| 维度 | 检查项 | 权重 |
|------|--------|------|
| 结构完整性 | YAML 头部、工作流程、错误处理 | 20% |
| 命名规范 | kebab-case、描述清晰度、角色前缀 | 15% |
| 选型合理性 | 组件类型选择、Subagent skills 配置 | 10% |
| 权限设计 | context/tools 一致性、最小权限 | 15% |
| 文档质量 | 注释、示例、引用 | 15% |
| 最佳实践 | 错误处理、边界条件 | 10% |
| 证据链完整性 | 能力需求表、Skill映射表、验证清单 | 15% |

**输出**: 各维度得分和问题列表
**错误处理**: 单个维度失败不影响整体

### Step 3.5: 命名和选型规范检查
**目标**: 验证组件命名和选型的合规性
**操作**:
1. 检查 Skill 角色前缀 (cmd-/std-/lib-)
   - cmd- 前缀用于入口型 Skill
   - std- 前缀用于自动发现型 Skill
   - lib- 前缀用于参考型 Skill
2. 检查命名格式 (kebab-case)
3. 验证组件选型决策是否合理
   - 入口型 Skill 是否真的需要用户手动触发
   - 自动发现型 Skill 的 description 是否清晰说明适用场景
   - 参考型 Skill 是否确实是专业知识库
4. 检查 Subagent 的 skills: 字段配置
   - 是否使用完整命名空间 (plugin:skill-name)
   - 引用的 Skill 是否存在
**输出**: 命名和选型检查结果
**错误处理**: 命名或选型不符合规范时记录为高严重度问题
### Step 4: 证据链完整性检查
**目标**: 验证设计文档的可追溯性
**操作**:
1. 检查是否包含能力需求表（工作流→能力→输入输出）
2. 检查是否包含Skill映射表（能力→Skill→状态）
3. 验证引用的skill是否存在或有创建计划
4. 检查验证清单是否完整
**输出**: 证据链检查结果
**错误处理**: 证据链缺失时记录为中等严重度问题

### Step 5: 深度模式匹配
**目标**: 识别复杂的架构反模式
**操作**: 使用 Grep 和 Glob 进行跨文件分析：

1. **隐式依赖检测**: 搜索未声明的 agent 调用
2. **循环依赖检测**: 构建调用图检测环路
3. **工具滥用检测**: 识别工具的不当使用模式
4. **代码重复检测**: 搜索相似的代码模式

**输出**: 深度分析问题列表
**错误处理**: 跨文件分析失败时降级为单文件分析

### Step 6: 生成综合报告
**目标**: 输出包含评分和详细问题的审阅报告
**操作**:
1. 汇总所有维度得分
2. 计算加权综合分数
3. 按严重程度排序问题
4. 生成 JSON 和 Markdown 双格式输出
**输出**: 综合审阅报告
**错误处理**: 报告生成失败时返回原始数据

## Input Format

### 基本输入
```
<file-path> [options]
```

### 输入示例
```
agents/advisor/advisor-core/SKILL.md
```

```
agents/reviewer/review-core/SKILL.md --depth=full
```

### 结构化输入 (可选)
```yaml
review:
  target: "agents/advisor/advisor-core/SKILL.md"
  options:
    depth: "full"        # shallow|full|deep
    includeInfo: true    # 是否包含 INFO 级别
    skipDimensions: []   # 跳过的检查维度
```

## Output Format

### 标准输出结构
```json
{
  "target": "agents/advisor/advisor-core/SKILL.md",
  "componentType": "skill",
  "status": "COMPLETED",
  "overallScore": 87,
  "dimensionScores": {
    "structure": 95,
    "naming": 90,
    "permissions": 85,
    "documentation": 80,
    "bestPractices": 75
  },
  "summary": {
    "errorCount": 0,
    "warningCount": 3,
    "infoCount": 5
  },
  "issues": [
    {
      "id": "SKILL-003",
      "severity": "WARNING",
      "dimension": "documentation",
      "location": {"line": 45, "column": 1},
      "description": "工作流步骤缺少错误处理说明",
      "suggestion": "为每个步骤添加错误处理策略",
      "codeSnippet": "### Step 3: 生成推荐方案"
    }
  ],
  "antipatternsMatched": [
    {
      "id": "SKILL-003",
      "name": "缺少错误处理",
      "confidence": 0.85
    }
  ],
  "metadata": {
    "linesOfCode": 180,
    "processingTime": "2.3s",
    "rulesApplied": 25
  }
}
```

### Markdown 输出示例
```markdown
# 智能审阅报告

## 基本信息
| 项目 | 值 |
|------|-----|
| 目标文件 | agents/advisor/advisor-core/SKILL.md |
| 组件类型 | Skill |
| 综合分数 | 87/100 |
| 状态 | COMPLETED |

## 维度评分
```
结构完整性    ████████████████████░ 95/100
命名规范      ██████████████████░░ 90/100
权限设计      █████████████████░░░ 85/100
文档质量      ████████████████░░░░ 80/100
最佳实践      ███████████████░░░░░ 75/100
```

## 问题摘要
| 严重程度 | 数量 |
|----------|------|
| ERROR | 0 |
| WARNING | 3 |
| INFO | 5 |

## 详细问题

### WARNING (3)

#### SKILL-003: 缺少错误处理说明
- **维度**: 文档质量
- **位置**: 第 45 行，Step 3
- **描述**: 工作流步骤缺少错误处理说明
- **建议**: 为每个步骤添加错误处理策略
```markdown
### Step 3: 生成推荐方案
**目标**: 输出具体的架构推荐
**操作**: 基于决策树结果生成推荐
**错误处理**: 推荐冲突时说明权衡并提供选择建议
```
```


## Error Handling

关键错误处理策略：

| 场景 | 处理 |
|------|------|
| 组件 SKILL.md 不存在 | 记录错误，继续其他 |
| 规则文件缺失 | 使用内置默认规则 |
| 评估超时 | 标记 timeout，继续其他 |
| 输出写入失败 | 重试后返回内存结果 |

> 详细错误处理：references/error-handling.txt（如果存在）

## Examples

| 场景 | 输出 |
|------|------|
| 单组件 review | 详细评估报告 |
| 批量 review | 汇总统计 + 详情 |
| 迭代 review | 对比前次结果 |
| 深度 review | 多轮评估 |

> 详细示例：references/examples.txt（如果存在）

## Notes

### Best Practices

1. 76+ 反模式规则覆盖
2. 7 个评估维度
3. 容错处理
4. 详细证据
5. 建议具体

### Integration

```
CCC Workflow → Review Core → 修复 → 再 Review
```

### Files

- 输入：`agents/{component-path}/SKILL.md`
- 输出：`docs/reviews/{component-name}-review.md`
