---
name: ccc:cmd-implement
model: sonnet
context: fork
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
description: "执行迭代计划，应用增量变更。触发：执行/应用/实施。支持整体/分阶段/预览模式。代码迭代第2步。"
argument-hint: "--plan=<iteration-plan-path> [--phase=<phase-number>] [--dry-run]"
---

# /ccc:implement

**完整流程**: `design-iterate` → **implement** → `review` → `fix`

Implements iteration plans from design-iterate, applying changes incrementally with validation and rollback support.

## 模型要求

- **推荐**: Claude Sonnet 4.5+ (高效能,最佳性价比)
- **可用**: Claude Opus 4.5+ (最高质量,复杂重构)
- **最小**: Claude Sonnet 4.5+ (最低要求)

### 功能需求
- 需要支持 Tool Use (Bash, Read, Write, Edit, Glob, Grep)
- 需要支持多轮对话和代码重构
- 需要处理迭代计划和增量变更
- 建议上下文窗口 >= 200K tokens (处理完整重构计划)

## SubAgents 协作

本工作流使用以下 SubAgents 进行任务执行：

### 核心 Agents
- **ccc:planner-core**: 计划解析器，读取和解析迭代计划文档

### 调度策略
- **串行执行**: cmd-implement → ccc:planner-core → 执行变更步骤
- **并行执行**: 无（增量变更需按顺序执行）
- **错误处理**: 任何步骤失败时支持回滚到上一个稳定状态

### Agent 输入输出
| Agent | 输入 | 输出 |
|-------|------|------|
| ccc:planner-core | 迭代计划文档路径 | 解析后的执行步骤和依赖关系 |

### 调用示例
```
用户: /ccc:implement --plan=docs/designs/my-refactor.md
  ↓
cmd-implement 读取计划文档
  ↓
调用 ccc:planner-core (解析计划和依赖)
  ↓
逐步执行变更:
  Step 1: 验证当前状态
  Step 2: 应用变更 (Phase 1)
  Step 3: 运行测试
  Step 4: 应用变更 (Phase 2)
  ...
  ↓
cmd-implement 生成实施报告
```

## Usage

```bash
# Implement entire plan
/ccc:implement --plan=docs/designs/my-refactor.md

# Implement specific phase
/ccc:implement --plan=docs/designs/my-refactor.md --phase=1

# Dry run (preview changes)
/ccc:implement --plan=docs/designs/my-refactor.md --dry-run
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--plan` | Yes | Path to iteration plan document |
| `--phase` | No | Specific phase number to implement |
| `--dry-run` | No | Preview changes without applying |

## Workflow

1. **Load Plan** - Parse iteration plan document
2. **Validate Context** - Check current state matches plan assumptions
3. **Apply Changes** - Execute modifications incrementally
4. **Verify** - Run tests and validation checks
5. **Generate Report** - Create implementation report

## Output

### Console Output

```
Implementation Complete: my-refactor

Phases Executed: 3/3
Files Modified: 12
Tests Passed: ✓

Implementation report: docs/implementations/2026-03-10-my-refactor-impl.md
```

### Implementation Report

| Attribute | Value |
|-----------|-------|
| **Directory** | `docs/implementations/` |
| **Filename** | `YYYY-MM-DD-<plan-name>-impl.md` |
| **Format** | Markdown |

## Examples

### Example 1: 实施完整的重构计划

```bash
/ccc:implement --plan=docs/designs/component-extraction.md
```

**场景**: 将混杂的代码重构为模块化组件

**输入**: 包含 3 个阶段的迭代计划（提取接口、创建实现、更新调用方）

**执行过程**:
1. 验证当前代码状态与计划假设一致
2. 阶段 1: 提取接口定义到独立文件
3. 阶段 2: 创建实现类并迁移逻辑
4. 阶段 3: 更新所有调用方使用新接口
5. 运行测试套件验证功能正常
6. 生成实施报告

**输出文件**:
- 修改 12 个源文件
- `docs/implementations/2026-03-10-component-extraction-impl.md`

### Example 2: 分阶段实施（仅执行第一阶段）

```bash
/ccc:implement --plan=docs/designs/database-migration.md --phase=1
```

**场景**: 大型数据库迁移分阶段执行，避免风险

**用例**: 计划包含 5 个阶段，先执行第 1 阶段（添加新列），验证后再执行后续阶段

**输出**:
```
Implementation Complete: database-migration (Phase 1/5)

Phase 1 Executed: Add migration columns
Files Modified: 3
Tests Passed: ✓

Next: Run /ccc:implement --plan=docs/designs/database-migration.md --phase=2
```

### Example 3: 预览模式（Dry Run）

```bash
/ccc:implement --plan=docs/designs/api-refactor.md --dry-run
```

**场景**: 在正式执行前预览将要进行的修改

**输出**:
```
DRY RUN: api-refactor

Planned Changes:
  Phase 1: Rename endpoints
    - src/api/routes.ts: 8 changes
    - src/api/handlers.ts: 12 changes

  Phase 2: Update request schemas
    - src/schemas/request.ts: 5 changes
    - tests/api.test.ts: 15 changes

Files to modify: 4
Estimated changes: 40

Run without --dry-run to apply changes
```

### Example 4: 处理阶段依赖关系

```bash
/ccc:implement --plan=docs/designs/multi-module-upgrade.md --phase=3
```

**场景**: 尝试执行第 3 阶段，但第 1、2 阶段尚未完成

**输出**:
```
Error: Phase dependency not satisfied

Phase 3 "Integrate modules" requires:
  ✗ Phase 1: Update core module (not completed)
  ✗ Phase 2: Update util module (not completed)

Suggestion: Run without --phase to execute in order
```

## Error Handling

| Error | Handling |
|-------|----------|
| Plan file not found | Display error with path |
| State mismatch | Show diff and ask for confirmation |
| Test failure | Rollback changes and report |
| Phase dependency | Execute dependencies first |
