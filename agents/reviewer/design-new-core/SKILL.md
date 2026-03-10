---
name: design-new-core
description: "设计新组件核心：协调 5 阶段设计流程→从零创建完整方案→关键决策透明。触发：新建设计/从零开始/design-new/core"
context: fork
model: sonnet
allowed-tools:
  - Read
  - Write
  - Bash
  - Task
skills:
  - ccc:std-component-selection
  - ccc:lib-design-patterns
  - ccc:std-evidence-chain
---

# Design New Core

## Purpose

Design New Core 是新建设计协调组件，负责从零开始协调完整的 5 阶段设计流程 (需求分析→架构选型→详细设计→规范验证→实施规划)，创建全新的组件设计方案。本组件确保关键决策透明可追溯，适合 Greenfield 项目或全新功能开发。

## Workflow

### Step 1: 接收新建请求
**目标**: 解析新建设计请求
**操作**:
1. 读取用户需求描述
2. 识别项目上下文
3. 确定设计范围 (单组件/多组件)
4. 验证输入完整性
**输出**: 新建设计请求规格
**错误处理**: 需求模糊时生成澄清问题

### Step 2: Stage 1 - 需求分析协调
**目标**: 执行需求分析阶段
**操作**:
1. 调用 requirement-core 进行 5Why 分析
2. 等待需求分析完成
3. 读取 stage-1-requirement.md
4. 验证需求分析质量
**输出**: Stage 1 输出
**错误处理**: 需求分析失败时重试或请求人工介入

### Step 3: Stage 2 - 架构选型协调
**目标**: 执行架构选型阶段
**操作**:
1. 调用 architect-core 进行架构决策
2. 等待架构选型完成
3. 读取 stage-2-architecture.md
4. 验证架构决策合理性
**输出**: Stage 2 输出
**错误处理**: 架构决策冲突时提供备选方案

### Step 4: Stage 3 - 详细设计协调
**目标**: 执行详细设计阶段
**操作**:
1. 调用 design-core 进行详细设计
2. 等待设计完成
3. 读取 stage-3-detailed-design.md
4. 验证设计完整性（包括证据链）
**输出**: Stage 3 输出
**错误处理**: 设计不完整时补充缺失部分

### Step 4.5: 验证证据链完整性
**目标**: 确保设计包含完整的可追溯证据链
**操作**:
1. 检查是否包含能力需求表
2. 检查是否包含Skill映射表
3. 验证所有引用的skill存在或有创建计划
4. 检查验证清单是否完整
**输出**: 证据链验证报告
**错误处理**: 证据链不完整时要求design-core补充

### Step 5: Stage 4 - 规范验证协调
**目标**: 执行规范验证阶段
**操作**:
1. 调用 validator-core 进行规范验证
2. 等待验证完成
3. 读取 stage-4-validation.md
4. 处理验证发现的问题
**输出**: Stage 4 输出
**错误处理**: 验证失败时返回 Stage 3 修正

### Step 6: Stage 5 - 实施规划协调
**目标**: 执行实施规划阶段
**操作**:
1. 调用 planner-core 进行实施规划
2. 等待规划完成
3. 读取 stage-5-implementation.md
4. 验证规划可行性
**输出**: Stage 5 输出
**错误处理**: 规划不可行时调整任务分解

### Step 7: 生成完整设计方案
**目标**: 整合 5 阶段输出为完整方案
**操作**:
1. 合并所有阶段输出
2. 生成执行摘要
3. 标注关键决策点
4. 写入完整设计文档
**输出**: 完整设计方案
**错误处理**: 整合失败时保留各阶段独立输出

## Input Format

### 基本输入
```
<user-requirement> [project-context]
```

### 输入示例
```
创建一个代码审查 SubAgent，自动检查代码规范并生成报告
```

```
创建一个技能，可以快速查找项目中的 TODO 注释并按优先级排序
@docs/project-context.md
```

### 结构化输入 (可选)
```yaml
design:
  requirement: "创建代码审查 SubAgent"
  context:
    projectPath: "/Users/xqh/project"
    existingComponents: []
    constraints:
      - "只读操作"
      - "支持多文件"
  options:
    depth: "full"         # full|quick
    autoValidate: true    # 自动验证
    outputFormat: "markdown"
```

## Output Format

### 标准输出结构
```json
{
  "projectId": "new-design-2024-03-01-001",
  "status": "COMPLETED",
  "stages": {
    "stage1": {
      "status": "COMPLETED",
      "output": "docs/designs/code-reviewer/stage-1-requirement.md",
      "score": 90
    },
    "stage2": {
      "status": "COMPLETED",
      "output": "docs/designs/code-reviewer/stage-2-architecture.md",
      "score": 88
    },
    "stage3": {
      "status": "COMPLETED",
      "output": "docs/designs/code-reviewer/stage-3-detailed-design.md",
      "score": 92
    },
    "stage4": {
      "status": "COMPLETED",
      "output": "docs/designs/code-reviewer/stage-4-validation.md",
      "score": 95
    },
    "stage5": {
      "status": "COMPLETED",
      "output": "docs/designs/code-reviewer/stage-5-implementation.md",
      "score": 85
    }
  },
  "keyDecisions": [
    {
      "stage": "stage2",
      "decision": "选择 SubAgent 而非 Skill",
      "reason": "需要多步骤工作流和 Task 协调"
    },
    {
      "stage": "stage3",
      "decision": "选择 Pipeline-Processor 模式",
      "reason": "审查流程为典型流水线"
    }
  ],
  "finalOutput": "docs/designs/code-reviewer/complete-design.md"
}
```

### Markdown 输出示例
```markdown
# 完整设计方案

## 项目信息
- **名称**: code-reviewer
- **类型**: SubAgent
- **创建时间**: 2024-03-01
- **状态**: 设计完成

## 执行摘要
本设计方案创建了一个代码审查 SubAgent，采用 Pipeline-Processor 模式，
包含 5 个处理步骤，使用 sonnet 模型执行，需要 fork 上下文。

## 5 阶段输出

### Stage 1: 需求分析
- 5Why 分析：提高代码审查效率
- 复杂度：complex
- 约束：需要写权限、多步骤

### Stage 2: 架构选型
- 组件类型：SubAgent
- 设计模式：Pipeline-Processor
- 模型：sonnet

### Stage 3: 详细设计
- YAML 配置：完整
- 工作流：5 步骤
- 工具：Read, Write, Bash, Task

### Stage 4: 规范验证
- 验证状态：PASSED
- 分数：95/100
- 问题：0 ERROR, 2 WARNING

### Stage 5: 实施规划
- 任务分解：12 个任务
- 总估算：90 分钟
- 风险等级：中

## 关键决策

### 决策 1: 选择 SubAgent 而非 Skill
**阶段**: Stage 2
**理由**:
- 需要调用多个子任务
- 涉及多步骤工作流
- 需要 Task 工具协调

### 决策 2: Pipeline-Processor 模式
**阶段**: Stage 3
**理由**:
- 审查流程为典型流水线
- 各步骤独立可测
- 易于扩展新检查项

## 设计文件
- [Stage 1](docs/designs/code-reviewer/stage-1-requirement.md)
- [Stage 2](docs/designs/code-reviewer/stage-2-architecture.md)
- [Stage 3](docs/designs/code-reviewer/stage-3-detailed-design.md)
- [Stage 4](docs/designs/code-reviewer/stage-4-validation.md)
- [Stage 5](docs/designs/code-reviewer/stage-5-implementation.md)
```


## Error Handling

关键错误处理策略：

| 场景 | 处理 |
|------|------|
| blueprint 不存在 | 提示先完成 blueprint |
| 依赖技能缺失 | 提示先创建依赖 |
| 工作流不连贯 | 指出断点和缺失命令 |
| 工具权限冲突 | 说明冲突详情 |

> 详细错误处理：references/error-handling.txt（如果存在）

## Examples

| 场景 | 输出 |
|------|------|
| 新技能设计 | SKILL.md + commands/ |
| SubAgent 设计 | agents/ + skill 文件 |
| 工作流设计 | 完整调用链 |
| 依赖设计 | 入口命令 + 工作流 |

> 详细示例：references/examples.txt（如果存在）

## Notes

### Best Practices

1. 从 blueprint 逆向推导
2. 工作流连贯性优先
3. 工具权限最小化
4. 依赖显式声明

### Integration

```
Stage 2 (Architect) → Stage 3 (Design-New-Core) → Stage 4 (Validator)
```

### Files

- 输入：`docs/blueprints/{project-name}/stage-2-architecture.md`
- 输出：`agents/{agent-name}/SKILL.md` + `commands/`
