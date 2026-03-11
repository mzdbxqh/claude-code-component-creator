---
name: ccc:cmd-review-workflow
model: sonnet
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
description: "工作流审阅 | 场景: 独立工具"
argument-hint: "[--artifact-id=<id>] [--depth=shallow|full]"
---

# /ccc:review-workflow

Reviews multiple components in workflow order, generating workflow health report with dependency analysis and parallelization opportunities.

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--artifact-id` | 指定 blueprint artifact | 当前上下文 |
| `--depth` | 审查深度 | full |

## 工作流程

### 步骤 1: 识别工作流

```bash
/ccc:review-workflow --artifact-id=BLP-001
```

系统加载 blueprint 并识别工作流：
```
加载 Blueprint: docs/ccc/blueprint/2026-03-03-BLP-001.yaml

识别工作流:
  - Phase 1: Intent (1 个组件)
  - Phase 2: Design (3 个组件)
  - Phase 3: Build (1 个组件)

共 5 个组件待审查
```

### 步骤 2: 按顺序审查

```
审查进度:

Phase 1: Intent
  ✓ intent-core (SubAgent) - 评分：85/100

Phase 2: Design
  ✓ advisor-core (SubAgent) - 评分：78/100
  ✓ architect-core (SubAgent) - 评分：82/100
  ✓ design-core (SubAgent) - 评分：75/100

Phase 3: Build
  ✓ delivery-core (SubAgent) - 评分：88/100
```

### 步骤 3: 分析依赖关系

```
依赖链分析:
  intent-core → advisor-core: ✅ (工具权限一致)
  advisor-core → architect-core: ✅ (模型兼容)
  architect-core → design-core: ⚠️ (调用深度 +1)
  design-core → delivery-core: ✅ (无问题)

识别并行机会:
  - Design 阶段：advisor-core 和 architect-core 可并行
  - 预计节省时间：30 秒
```

### 步骤 4: 生成健康度报告

```
工作流健康度报告已生成:
  docs/reviews/2026-03-03-BLP-001-workflow-review.md

总体评分：82/100 (Grade: B)
```

## 输出规范

### 工作流健康度报告

| 属性 | 值 |
|------|-----|
| **目录** | `docs/reviews/` |
| **文件名** | `YYYY-MM-DD-<artifact-id>-workflow-review.md` |
| **格式** | Markdown |

### 报告结构

| 章节 | 内容 |
|------|------|
| 工作流概览 | Phase 列表、组件总数 |
| 工作流完整性 | 每个 phase 的完整性检查 |
| 阶段交接清晰度 | 输入输出定义检查 |
| 依赖关系健康度 | 调用链分析结果 |
| 并行化机会 | 可并行的组件列表 |
| 总体评分 | 综合健康度评分 |

## 健康度指标

### 工作流完整性

| 状态 | 说明 |
|------|------|
| ✅ | 所有 phase 都有明确的入口和出口 |
| ⚠️ | 部分 phase 缺少入口或出口定义 |
| ❌ | 关键 phase 缺失 |

### 阶段交接清晰度

| 状态 | 说明 |
|------|------|
| ✅ | 所有 phase 的输入输出明确定义 |
| ⚠️ | 部分 phase 输入输出不明确 |
| ❌ | 输入输出未定义 |

### 依赖关系健康度

| 检查项 | 通过标准 |
|--------|----------|
| 工具权限 | 调用者拥有被调用者需要的工具 |
| 模型兼容 | 父子组件模型选择合理 |
| 调用深度 | 调用链深度 < 5 层 |
| 循环依赖 | 无循环调用 |

## 错误处理

| 错误场景 | 处理方式 |
|----------|----------|
| Blueprint 不存在 | 提示检查 artifact-id |
| 无工作流定义 | 返回错误，建议添加 workflow 章节 |
| 组件文件不存在 | 标记为 missing，继续审查其他 |
| 审查超时 | 返回已完成的审查结果 |

## 示例

### 示例 1: 基本使用

```bash
/ccc:review-workflow --artifact-id=BLP-001
```

### 示例 2: 快速审查 (跳过架构分析)

```bash
/ccc:review-workflow --artifact-id=BLP-001 --depth=shallow
```

### 示例 3: 完整审查 (含架构分析)

```bash
/ccc:review-workflow --artifact-id=BLP-001 --depth=full
```

### 示例 4: 与审查命令连用

```bash
# 先审查单个组件
/ccc:review --artifact-id=DLV-001

# 再审查整个工作流
/ccc:review-workflow --artifact-id=BLP-001
```

## 报告摘例

```markdown
# 工作流健康度报告：BLP-001

## 工作流概览

- 工作流名称：CCC Review System
- Phase 总数：3
- 组件总数：5
- 审查时间：2026-03-03

## 工作流完整性

| Phase | 入口 | 出口 | 组件数 | 状态 |
|-------|------|------|--------|------|
| Intent | 用户需求 | intent.yaml | 1 | ✅ |
| Design | intent.yaml | blueprint.yaml | 3 | ✅ |
| Build | blueprint.yaml | delivery/ | 1 | ✅ |

完整性评分：100% ✅

## 阶段交接清晰度

| 交接点 | 输入 | 输出 | 状态 |
|--------|------|------|------|
| Intent→Design | 用户需求 | intent.yaml | ✅ |
| Design→Build | intent.yaml | blueprint.yaml | ⚠️ (缺少验证步骤) |

交接清晰度评分：85% ⚠️

## 依赖关系健康度

调用链分析:
- intent-core → advisor-core: ✅
- advisor-core → architect-core: ✅
- architect-core → design-core: ⚠️ (调用深度 +1)
- design-core → delivery-core: ✅

依赖健康度评分：90% ⚠️

## 并行化机会

可并行的组件:
- Design 阶段：advisor-core, architect-core
- 预计节省时间：30 秒

## 总体评分

(100 + 85 + 90) / 3 = 92% (Grade: A-)
```

## 下一步建议

审查完成后提示：
1. 查看完整报告：`cat docs/reviews/YYYY-MM-DD-<artifact-id>-workflow-review.md`
2. 修复发现的问题：`/ccc:fix --artifact-id=<artifact-id>`
3. 优化并行化：考虑将可并行的组件改为并行执行
