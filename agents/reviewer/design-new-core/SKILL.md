---
name: design-new-core
description: "设计新组件核心：协调 5 阶段设计流程→从零创建完整方案→关键决策透明。触发：新建设计/从零开始/design-new/core"
model: sonnet
tools:
  - Read
  - Write
  - Bash
  - Agent
permissionMode: prompt
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
1. 调用 ccc:requirement-core 进行 5Why 分析
2. 等待需求分析完成
3. 读取 stage-1-requirement.md
4. 验证需求分析质量
**输出**: Stage 1 输出
**错误处理**: 需求分析失败时重试或请求人工介入

### Step 3: Stage 2 - 架构选型协调
**目标**: 执行架构选型阶段
**操作**:
1. 调用 ccc:architect-core 进行架构决策
2. 等待架构选型完成
3. 读取 stage-2-architecture.md
4. 验证架构决策合理性
**输出**: Stage 2 输出
**错误处理**: 架构决策冲突时提供备选方案

### Step 4: Stage 3 - 详细设计协调
**目标**: 执行详细设计阶段
**操作**:
1. 调用 ccc:design-core 进行详细设计
2. 等待设计完成
3. 读取 stage-3-detailed-design.md
4. 验证设计完整性（包括证据链）
**输出**: Stage 3 输出
**错误处理**: 设计不完整时补充缺失部分

### Step 4.2: 设计组件元数据（新增）
**目标**: 根据组件类型生成推荐的元数据模板（三层防护体系-设计环节）

**操作**:

```python
def designComponentMetadata(component_type, workflow_position=None):
    """
    根据组件类型生成推荐的元数据模板

    Args:
        component_type: 'cmd-skill' | 'std-skill' | 'lib-skill' | 'agent'
        workflow_position: {'type': 'main', 'step': 2, 'input': 'intent', 'output': 'blueprint'}

    Returns:
        metadata_template: 推荐的description和其他元数据
    """
    if component_type == 'cmd-skill':
        if workflow_position:
            # 主工作流或迭代流程
            if workflow_position['type'] == 'main':
                description = f"主工作流第{workflow_position['step']}步。{{核心功能}}。"
            elif workflow_position['type'] == 'iteration':
                description = f"代码迭代流程第{workflow_position['step']}步。{{核心功能}}。"

            # 添加输入输出关系
            if workflow_position.get('input'):
                description += f"承接{workflow_position['input']}，"
            if workflow_position.get('output'):
                description += f"输出给{workflow_position['output']}。"
        else:
            # 独立工具
            description = "独立工具。{核心功能}，无前后依赖。"

        return {
            'description': description,
            'argument-hint': '<必需参数> [可选参数]',
            'allowed-tools': ['Read', 'Write', 'Edit', 'Bash'],
            'model': 'sonnet',
            'context': 'fork'
        }

    elif component_type == 'std-skill':
        return {
            'description': '{知识类型}。当{触发场景}时，{动作词}{对象}。{应用范围}。',
            'model': 'sonnet',
            'allowed-tools': [],
            'context': 'main',
            'examples': [
                '组件选型决策规则。当设计或审阅插件时，判断应使用cmd-/std-/lib-哪种Skill类型。',
                '命名规范检查标准。当创建或审阅组件时，验证命名是否符合Skill/Subagent规范。'
            ]
        }

    elif component_type == 'lib-skill':
        return {
            'description': '{知识库类型}，{数量}定义覆盖{范围}。由Subagent通过skills字段加载。{用途}。',
            'model': 'haiku',  # lib-* 通常用haiku即可
            'allowed-tools': [],
            'context': 'main',
            'examples': [
                '反模式知识库，84个定义覆盖8维度。由Subagent通过skills字段加载。用于质量检查。',
                '设计模式知识库，CCC 5阶段设计流程模式。由Subagent通过skills字段加载。用于架构设计。'
            ]
        }

    # 其他类型（agent等）
    return {}
```

**输出**:
- 在设计文档中添加"推荐的元数据模板"章节
- 包含description示例和填写指导

**错误处理**: 如果组件类型未识别，提供通用模板

**示例输出**（在设计文档中）:

```markdown
## 组件元数据设计

### cmd-analyze (入口型Skill)

**推荐元数据**:
```yaml
name: cmd-analyze
description: "主工作流第2步。分析代码质量并生成报告。承接init的项目路径，输出分析报告给review。"
argument-hint: "<project-path> [--depth=shallow|deep]"
model: sonnet
context: fork
allowed-tools: [Read, Grep, Bash]
```

**说明**:
- ✅ description说明了工作流位置（第2步）
- ✅ description说明了输入（init的项目路径）和输出（分析报告给review）
- ❌ description没有包含触发词（用户直接调用# /ccc:analyze (示例命令)，不需要）

**如果改为std-* skill**（供参考）:
```yaml
name: std-code-quality-rules
description: "代码质量检查规则。当分析代码时，验证是否符合最佳实践和安全标准。"
```
```

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
1. 调用 ccc:validator-core 进行规范验证
2. 等待验证完成
3. 读取 stage-4-validation.md
4. 处理验证发现的问题
**输出**: Stage 4 输出
**错误处理**: 验证失败时返回 Stage 3 修正

### Step 6: Stage 5 - 实施规划协调
**目标**: 执行实施规划阶段
**操作**:
1. 调用 ccc:planner-core 进行实施规划
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
