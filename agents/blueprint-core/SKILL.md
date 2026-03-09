---
name: blueprint-core
description: "蓝图生成 (Blueprint)：从 Intent 到完整设计→5 阶段流程 (需求→架构→设计→验证→规划)。触发：蓝图/设计/方案/规划/blueprint"
argument-hint: "<intent-path> [options]"
context: fork
model: sonnet
allowed-tools:
  - Read
  - Write
  - Bash
  - Task
---

# blueprint-core Subagent

## Purpose

Blueprint Core 是 CCC 工作流的 Stage 2 核心组件，负责从 Intent 制品生成完整的 5 阶段设计蓝图。本组件协调 5 个子阶段 (需求分析→架构选型→详细设计→规范验证→实施规划)，生成可直接交付的设计规格文档。

## Workflow

### Step 1: 加载 Intent 制品
**目标**: 读取并解析 Intent 输入
**操作**:
1. 读取 intent-path 指定的 Intent 文件
2. 解析 YAML 格式的需求、约束、决策
3. 验证 Intent 文件完整性
**输出**: 结构化的 Intent 数据
**错误处理**: 文件不存在时提示检查路径

### Step 2: 阶段 1-需求分析
**目标**: 深化需求理解
**操作**:
1. 调用 requirement-core 进行 5Why 分析
2. 生成需求澄清矩阵 (5W1H)
3. 输出 stage-1-requirement.md
**输出**: Stage 1 需求规格
**错误处理**: 需求模糊时生成澄清问题

### Step 3: 阶段 2-架构选型
**目标**: 选择合适的架构模式
**操作**:
1. 调用 architect-core 基于需求选择组件类型
2. 匹配设计模式 (Pipeline/Recursive/Interactive 等)
3. 规划工具权限和模型选择
4. 输出 stage-2-architecture.md
**输出**: Stage 2 架构决策
**错误处理**: 无匹配模式时建议自定义

### Step 4: 阶段 3-详细设计
**目标**: 生成具体实现设计
**操作**:
1. 调用 design-core 设计 YAML 配置
2. 设计工作流步骤 (Step 1-N)
3. 规划文件引用和错误处理策略
4. 输出 stage-3-detailed-design.md
**输出**: Stage 3 详细设计
**错误处理**: 设计不完整时提示补充

### Step 5: 阶段 4-规范验证
**目标**: 验证设计合规性
**操作**:
1. 调用 validator-core 对照 HANDBOOK 验证
2. 检查 YAML 配置、工作流、工具权限
3. 生成验证报告和问题列表
4. 输出 stage-4-validation.md
**输出**: Stage 4 验证报告
**错误处理**: 验证失败时提供修正建议

### Step 6: 阶段 5-实施规划
**目标**: 生成实施计划
**操作**:
1. 调用 planner-core 进行 WBS 任务分解
2. 估算时间和依赖关系
3. 识别风险和缓解措施
4. 输出 stage-5-implementation.md
**输出**: Stage 5 实施计划
**错误处理**: 计划不可行时调整

### Step 6.5: 阶段 5.5-测试规划【新增】
**目标**: 设计测试用例和测试框架
**操作**:
1. 基于 Stage 1 的验收标准设计测试用例
2. 规划测试类型（功能测试/边界测试/集成测试）
3. 生成测试模板文件路径
4. 输出 stage-5-5-test-plan.md
**输出**: Stage 5.5 测试规划文档
**错误处理**: 测试规划不完整时提供模板

### Step 7: 生成 Blueprint 制品
**目标**: 整合 5 阶段输出
**操作**:
1. 创建 `docs/ccc/blueprint/{date}-{artifact-id}.yaml`
2. 整合 5 个阶段的输出
3. 生成 Blueprint 摘要和导航
4. 验证文件写入成功
**输出**: Blueprint 制品文件
**错误处理**: 写入失败时重试 1 次

## Input Format

### 基本输入
```
<intent-path> [options]
```

### 输入示例
```
docs/ccc/intent/2026-03-03-INT-001.yaml
```

```
docs/ccc/intent/2026-03-03-INT-001.yaml --lang=zh-cn
```

### 结构化输入 (可选)
```yaml
blueprint:
  intentPath: "docs/ccc/intent/2026-03-03-INT-001.yaml"
  options:
    lang: "zh-cn"
    stages: ["all"]  # 或指定阶段
    outputPath: "docs/ccc/blueprint/"
```

## Output Format

### 标准输出结构
```json
{
  "artifactId": "BLP-2026-03-03-001",
  "status": "COMPLETED",
  "intentId": "INT-2026-03-03-001",
  "stages": {
    "stage1": {"status": "COMPLETED", "file": "stage-1-requirement.md"},
    "stage2": {"status": "COMPLETED", "file": "stage-2-architecture.md"},
    "stage3": {"status": "COMPLETED", "file": "stage-3-detailed-design.md"},
    "stage4": {"status": "COMPLETED", "file": "stage-4-validation.md"},
    "stage5": {"status": "COMPLETED", "file": "stage-5-implementation.md"}
  },
  "outputPath": "docs/ccc/blueprint/YYYY-MM-DD-BLP-xxx.yaml"
}
```

### Blueprint 摘要示例
```markdown
# Blueprint: TODO Finder Skill

## 制品信息
- **ID**: BLP-2026-03-03-001
- **Intent**: INT-2026-03-03-001
- **组件类型**: Skill
- **复杂度**: simple

## 5 阶段摘要

### Stage 1: 需求分析
- 核心目标：快速查找项目中的 TODO 注释
- 硬约束：只读操作、多文件支持
- 软约束：支持优先级排序

### Stage 2: 架构选型
- 设计模式：Search-Filter-Sort
- 上下文：main
- 模型：haiku
- 工具：Read, Grep

### Stage 3: 详细设计
- 工作流步骤：4 步
- 错误处理：覆盖完整
- 输出格式：Markdown 列表

### Stage 4: 规范验证
- 验证状态：PASSED
- 合规分数：95/100
- 警告：1 个

### Stage 5: 实施规划
- 任务分解：8 个任务
- 估算时间：30 分钟
- 风险等级：低

### Stage 5.5: 测试规划【新增】
- 测试类型：3 种（功能/边界/集成）
- 测试用例：5 个
- 测试框架：evals.json + README + fixtures

## 测试规划（Stage 5.5）

```yaml
testPlan:
  testTypes:
    - type: "功能测试"
      description: "验证核心功能是否工作"
      testCount: 3
    - type: "边界测试"
      description: "验证边界情况处理"
      testCount: 2
    - type: "集成测试"
      description: "与其他组件的交互"
      testCount: 1

  testFramework:
    structure: |
      tests/
        ├── unit/           # 单元测试
        │   └── test_xxx.py
        ├── integration/    # 集成测试
        │   └── test_xxx.md
        └── fixtures/       # 测试夹具
            └── sample_*.txt

    templatePath: "docs/templates/skill-test-template.md"

  executionCommand: "/xxx:test-sandbox"
```

## 下一步
运行 `/ccc:build --artifact-id=BLP-2026-03-03-001` 生成交付物
```

## Error Handling

| 错误场景 | 处理策略 | 示例 |
|----------|----------|------|
| Intent 文件不存在 | 提示检查路径 | "Intent 文件不存在：xxx" |
| Intent 格式错误 | 返回解析错误详情 | "YAML 解析失败：第 5 行" |
| 子阶段调用失败 | 重试 1 次，仍失败则跳过 | "Stage 2 调用失败，跳过此阶段" |
| 阶段间数据传递失败 | 使用默认值继续 | "Stage 1 输出不完整，使用默认值" |
| 验证失败 | 提供修正建议继续 | "验证失败：context 冲突，建议修改" |
| Blueprint 写入失败 | 重试 1 次，内存保存 | "写入失败，结果保存在内存中" |

## Examples

### Example 1: 简单 Skill 蓝图

**输入**:
```
docs/ccc/intent/2026-03-03-INT-001.yaml
```

**输出**:
```json
{
  "artifactId": "BLP-2026-03-03-001",
  "status": "COMPLETED",
  "stages": {
    "stage1": "COMPLETED",
    "stage2": "COMPLETED",
    "stage3": "COMPLETED",
    "stage4": "COMPLETED",
    "stage5": "COMPLETED"
  }
}
```

### Example 2: 复杂 SubAgent 蓝图

**输入**:
```
docs/ccc/intent/2026-03-03-INT-002.yaml
```

**输出**:
```markdown
# Blueprint: 代码审查 SubAgent

## 架构决策
- 组件类型：SubAgent
- 设计模式：Pipeline-Processor
- 上下文：fork
- 模型：sonnet
- 工具：Read, Write, Task, Bash

## 工作流设计
1. 读取变更文件
2. 检查编码规范
3. 运行单元测试
4. 生成审查报告

## 验证状态
- 合规分数：92/100
- 警告：2 个
```

### Example 3: 数据转换蓝图

**输入**:
```
docs/ccc/intent/2026-03-03-INT-003.yaml
```

**输出**:
```json
{
  "artifactId": "BLP-2026-03-03-003",
  "componentType": "Skill",
  "designPattern": "Transform-Validate",
  "stages": {
    "stage1": "COMPLETED",
    "stage2": "COMPLETED",
    "stage3": "COMPLETED",
    "stage4": "PASSED_WITH_WARNINGS",
    "stage5": "COMPLETED"
  }
}
```

### Example 4: 性能优化蓝图

**输入**:
```
docs/ccc/intent/2026-03-03-INT-004.yaml
```

**输出**:
```markdown
# Blueprint: 性能优化 SubAgent

## 复杂度评估
- 需求复杂度：complex
- 技术风险：中等
- 估算时间：90 分钟

## 架构模式
- Recursive-Analyzer (递归分析数据库查询)
- 模型：opus (深度推理)
```

### Example 5: 部分阶段蓝图

**输入**:
```
docs/ccc/intent/2026-03-03-INT-005.yaml --stages=stage1,stage2
```

**输出**:
```json
{
  "artifactId": "BLP-2026-03-03-005",
  "status": "PARTIAL",
  "completedStages": ["stage1", "stage2"],
  "skippedStages": ["stage3", "stage4", "stage5"],
  "note": "仅执行指定阶段"
}
```

## Notes

### Best Practices

1. **阶段顺序**: 严格遵循 5 阶段顺序，不可跳跃
   **为什么**: 每个阶段的输出是下一阶段的输入，跳跃会导致数据丢失和设计缺陷传播。例如，跳过验证阶段可能导致不合规的设计进入实施规划。
   **风险**: 高 - 设计缺陷会传递到交付物，增加后期修复成本

2. **数据传递**: 每阶段输出作为下一阶段输入
   **为什么**: 保证设计信息在阶段间完整传递，避免重复工作和信息丢失。使用结构化数据 (YAML/Markdown) 确保可解析性。
   **风险**: 高 - 数据丢失会导致后续阶段基于不完整信息做决策

3. **验证前置**: 验证不通过不进入实施规划
   **为什么**: 验证阶段发现设计缺陷的成本远低于实施后发现。前置验证确保只有合规设计进入实施阶段。
   **风险**: 高 - 不合规设计会生成需要返工的交付物

4. **文件组织**: 每阶段独立文件便于追踪
   **为什么**: 独立文件支持增量更新、版本控制和问题定位。便于审查每个阶段的决策和变更历史。
   **风险**: 中 - 文件混乱会增加维护成本

5. **摘要生成**: Blueprint 摘要包含关键决策
   **为什么**: 用户和后续工具需要快速理解设计要点而无需阅读完整文档。摘要支持快速导航和决策追溯。
   **风险**: 中 - 缺少摘要会降低用户体验和追溯效率

### Common Pitfalls

1. ❌ **阶段跳跃**: 跳过验证阶段直接规划
2. ❌ **数据丢失**: 阶段间传递丢失关键信息
3. ❌ **验证缺失**: 设计未经验证就实施
4. ❌ **文件混乱**: 阶段输出文件命名不规范
5. ❌ **摘要缺失**: 没有 Blueprint 摘要难以导航

### 5-Stage Workflow

```
Intent
  ↓
Stage 1: 需求分析 (requirement-core)
  ↓
Stage 2: 架构选型 (architect-core)
  ↓
Stage 3: 详细设计 (design-core)
  ↓
Stage 4: 规范验证 (validator-core)
  ↓
Stage 5: 实施规划 (planner-core)
  ↓
Blueprint Artifact
```

### Integration with CCC Workflow

```
Intent Core → Intent Artifact
    ↓
Blueprint Core (本组件) → 5 阶段设计
    ↓
Blueprint Artifact (docs/ccc/blueprint/)
    ↓
Delivery Core → 生成交付物
```

### File References

- 输入：`docs/ccc/intent/YYYY-MM-DD-INT-xxx.yaml`
- 输出：`docs/ccc/blueprint/YYYY-MM-DD-BLP-xxx.yaml`
- 阶段文件：`docs/designs/{project}/stage-{N}-{name}.md`
