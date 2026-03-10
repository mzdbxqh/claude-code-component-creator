---
name: planner-core
description: "实施规划 (Planner)：生成详细实施计划→任务分解 + 时间估算。原则：无计划不执行。触发：计划/实施/任务列表/planner/estimate"
argument-hint: "<stage-4-output-path>"
context: fork
model: sonnet
allowed-tools:
  - Read
  - Write
skills:
  - ccc:std-component-selection
---

# 实施规划核心

## Purpose

Planner 是 CCC 工作流的 Stage 5 实施规划核心组件，负责基于 Stage 4 验证通过的设计规格，生成详细的实施计划。包括任务分解、时间估算、依赖关系和风险控制，确保实施过程有序可控。

## Workflow

### Step 1: 读取 Stage 4 输出
**目标**: 加载验证通过的设计规格
**操作**:
1. 读取 `docs/designs/{project-name}/stage-4-validation.md`
2. 解析设计规格和验证结果
3. 提取约束条件和验收标准
**输出**: 结构化的设计数据
**错误处理**: 文件不存在或验证未通过时提示

### Step 2: 任务分解 (WBS)
**目标**: 将实施工作分解为可执行的任务单元
**操作**: 使用工作分解结构 (WBS) 方法：

```
Level 1: 项目实施
├── Level 2: 阶段 1 - 环境准备
│   ├── Level 3: 创建目录结构
│   ├── Level 3: 配置 YAML 头部
│   └── Level 3: 设置工具权限
├── Level 2: 阶段 2 - 核心逻辑
│   ├── Level 3: 实现 Step 1
│   ├── Level 3: 实现 Step 2
│   └── Level 3: 实现 Step 3
├── Level 2: 阶段 3 - 错误处理
│   ├── Level 3: 实现错误检测
│   └── Level 3: 实现错误恢复
└── Level 2: 阶段 4 - 测试验证
    ├── Level 3: 编写测试用例
    └── Level 3: 执行验收测试
```

**输出**: WBS 任务分解树
**错误处理**: 任务粒度过大时提示拆分

### Step 3: 时间估算
**目标**: 为每个任务估算实施时间
**操作**: 基于任务复杂度估算：

| 任务类型 | Simple | Medium | Complex |
|----------|--------|--------|---------|
| 文件创建 | 2 min | 5 min | 10 min |
| 逻辑实现 | 5 min | 15 min | 30 min |
| 错误处理 | 3 min | 10 min | 20 min |
| 测试编写 | 5 min | 15 min | 30 min |

使用三点估算法：
- 乐观时间 (O): 最佳情况
- 最可能时间 (M): 正常情况
- 悲观时间 (P): 最差情况
- 期望时间 (E): (O + 4M + P) / 6

**输出**: 时间估算表
**错误处理**: 估算不确定性高时标注范围

### Step 4: 依赖关系分析
**目标**: 识别任务间的依赖关系
**操作**: 构建任务依赖图：

```yaml
dependencies:
  - task: "实现核心逻辑"
    dependsOn: ["环境准备完成"]
  - task: "编写测试"
    dependsOn: ["核心逻辑完成"]
  - task: "验收测试"
    dependsOn: ["测试编写完成", "错误处理完成"]
```

**输出**: 任务依赖图
**错误处理**: 循环依赖时提示重新设计

### Step 5: 风险识别
**目标**: 识别实施过程中的潜在风险
**操作**: 从以下维度识别风险：

| 风险类型 | 检查项 | 缓解措施 |
|----------|--------|----------|
| 技术风险 | 新技术/复杂逻辑 | 预留调研时间 |
| 依赖风险 | 外部组件/服务 | 准备备选方案 |
| 时间风险 | 紧 deadline | 识别可裁剪范围 |
| 质量风险 | 高可靠性要求 | 增加测试覆盖 |

**输出**: 风险登记册
**错误处理**: 高风险无缓解措施时升级警报

### Step 6: 生成实施计划
**目标**: 输出完整的实施计划文档
**操作**:
1. 整合 WBS、时间估算、依赖关系
2. 生成甘特图或时间线
3. 创建 Stage 5 输出文件
**输出**: `docs/designs/{project-name}/stage-5-implementation.md`
**错误处理**: 写入失败时重试并报告

## Input Format

### 输入路径
```
<stage-4-output-path>
```

### Stage 4 输入示例
```markdown
# 规范验证报告

## 验证结果
状态：PASSED

## 设计规格
```yaml
---
name: todo-finder
description: "查找并排序 TODO 注释"
context: main
model: haiku
allowed-tools:
  - Read
  - Grep
---
```

## 工作流步骤
1. 解析搜索关键词
2. 使用 Grep 搜索
3. 提取优先级标记
4. 排序输出
```

### JSON 输入示例 (可选)
```json
{
  "validationStatus": "PASSED",
  "designSpec": {
    "name": "todo-finder",
    "workflowSteps": ["步骤 1", "步骤 2", "步骤 3"]
  },
  "constraints": ["只读操作", "多文件支持"]
}
```

## Output Format

### 标准输出结构
```json
{
  "implementationPlan": {
    "wbs": [
      {
        "id": "1.1.1",
        "name": "任务名称",
        "estimate": "5 min",
        "dependencies": []
      }
    ],
    "timeline": {
      "startDate": "2024-03-01",
      "endDate": "2024-03-01",
      "totalEstimate": "30 min"
    },
    "risks": [
      {
        "type": "技术风险",
        "description": "描述",
        "mitigation": "缓解措施"
      }
    ]
  }
}
```

### Markdown 输出示例
```markdown
# 实施计划文档

## 项目概述
- **项目名称**: todo-finder
- **总估算时间**: 30 分钟
- **风险等级**: 低

## 工作分解结构 (WBS)

### 阶段 1: 环境准备 (5 min)
- [ ] 1.1.1 创建 SKILL.md 文件结构 (2 min)
- [ ] 1.1.2 配置 YAML 头部 (3 min)

### 阶段 2: 核心逻辑 (15 min)
- [ ] 1.2.1 实现参数解析 (5 min)
- [ ] 1.2.2 实现 Grep 搜索 (5 min)
- [ ] 1.2.3 实现优先级排序 (5 min)

### 阶段 3: 错误处理 (5 min)
- [ ] 1.3.1 添加输入验证 (3 min)
- [ ] 1.3.2 添加错误提示 (2 min)

### 阶段 4: 测试验证 (5 min)
- [ ] 1.4.1 执行基本测试 (3 min)
- [ ] 1.4.2 验证输出格式 (2 min)

## 依赖关系
```
[1.1 环境准备] → [1.2 核心逻辑] → [1.3 错误处理] → [1.4 测试验证]
```

## 风险登记
| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| Grep 性能问题 | 低 | 中 | 限制搜索范围 |
```


## Error Handling

关键错误处理策略：

| 场景 | 处理 |
|------|------|
| Stage 4 文件不存在 | 提示先完成验证 |
| 验证失败 | 拒绝生成计划 |
| 任务依赖循环 | 检测并报告循环 |
| 输出写入失败 | 重试后返回内存结果 |

> 详细错误处理：references/error-handling.txt（如果存在）

## Examples

| 场景 | 输出 |
|------|------|
| 标准计划 | 5-7 个任务 |
| 简单功能 | 2-3 个任务 |
| 复杂重构 | 10+ 任务分批 |
| 有依赖 | 按依赖排序 |

> 详细示例：references/examples.txt（如果存在）

## Notes

### Best Practices

1. 任务 bite-sized（2-5 分钟）
2. 每任务有验证步骤
3. 频繁 commit
4. DRY/YAGNI/TDD

### Integration

```
Stage 4 (Validator) → Stage 5 (Planner) → 实施
```

### Files

- 输入：`docs/designs/{project-name}/stage-4-validation.md`
- 输出：`docs/plans/{project-name}-implementation-plan.md`
