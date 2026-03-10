# CCC 迭代设计最佳实践

## 概述

本文档定义使用 `/ccc:design-iterate` 进行大规模项目重构的最佳实践。

## 核心原则

### 1. 显式调用优先

**原则**: 凡需要1个以上私有标准skill支撑的工序，必须通过SubAgent显式引用skill，禁止依赖LLM隐式调用。

**示例**:
```yaml
# ✓ 正确：显式引用
subagent: design-core
skills:
  - skill-a
  - skill-b

# ✗ 错误：隐式依赖
description: "使用skill-a和skill-b完成任务"
```

### 2. 文件化审核

**原则**: 凡标注"人工审核"的阶段，必须输出标准格式文件作为阶段产物，存放于约定路径。

**路径规范**:
- 盘点结果: `docs/refactor/00-inventory.md`
- 迭代方案: `docs/refactor/01-plan-<name>.md`
- 实施报告: `docs/implementations/<date>-<name>-impl.md`

### 3. 上下文隔离

**原则**: 阶段间通过文件引用传递上下文，而非依赖对话历史。

**Token控制**:
- 单个command注入的skill总token需根据盘点结果合理控制
- 大规模项目建议单个阶段不超过50K tokens

### 4. 证据链完整

**原则**: 每个阶段的输入来源、输出产物、决策依据必须可追溯可评审。

**必需章节**:
- 能力需求表
- Skill映射表
- 验证清单

### 5. 规模适配

**原则**: 方案需能承载几十万行代码级别的项目，任何单个环节不得因产物规模增长而导致上下文溢出。

**策略**:
- 分phase执行
- 使用文件引用而非内联内容
- 增量加载而非全量加载

### 6. 先方案后执行

**原则**: 每个步骤先输出方案文件到 `docs/refactor/` 目录，经确认后再修改实际的skill/command/subagent配置文件。

**工作流**:
1. 生成方案 → `docs/refactor/01-plan.md`
2. 人工审核
3. 执行实施 → 使用 `/ccc:implement`

### 7. 增量变更

**原则**: 不要一次性重写所有文件，按阶段逐步重构。

**建议粒度**:
- Phase 1: 核心架构调整
- Phase 2: 接口适配
- Phase 3: 功能增强
- Phase 4: 优化清理

### 8. 占位机制

**原则**: 对于盘点后发现缺失的skill，先创建占位文件（含职责说明和预期输入输出），内容后补。

**占位文件模板**:
```markdown
---
name: skill-name
description: "[PLACEHOLDER] 职责说明"
status: placeholder
---

# Skill Name

## Purpose
[待补充]

## Expected Input
[待补充]

## Expected Output
[待补充]
```

## 使用流程

### 大规模项目重构

1. **盘点**: `/ccc:design-iterate` 自动执行Step 0
2. **审核**: 检查 `docs/refactor/00-inventory.md`
3. **规划**: 继续执行生成迭代方案
4. **审核**: 检查迭代方案文档
5. **实施**: `/ccc:implement --plan=<方案路径>`
6. **验证**: 运行测试，检查实施报告

### 单组件迭代

1. **迭代**: `/ccc:design-iterate <component-path>`（跳过Step 0）
2. **审核**: 检查迭代方案
3. **实施**: `/ccc:implement --plan=<方案路径>`

