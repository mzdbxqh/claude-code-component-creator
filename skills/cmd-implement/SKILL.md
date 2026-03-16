---
name: cmd-implement
model: sonnet
context: fork
disable-model-invocation: true
agent: ccc:delivery-core:delivery-core
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
description: "实现代码：从Blueprint首次实现或从iteration-plan增量变更。触发：实现/编码/执行。支持整体/分阶段/预览模式。开发流程第3步或迭代流程第2步。"
argument-hint: "--blueprint=<blueprint-path> | --plan=<iteration-plan-path> [--phase=<phase-number>] [--dry-run]"
---

# /cmd-implement

**开发流程**: `init` → `design` → **implement** → `review` → `fix` → `validate` → `build`
**迭代流程**: `design-iterate` → **implement** → `review` → `fix`

Implements code from Blueprint (initial implementation) or iteration plans (incremental changes), with validation and rollback support.

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

本工作流根据实现模式使用不同的 SubAgents：

### 模式 1: Blueprint 实现

- **ccc:blueprint-core**: Blueprint 解析器，提取组件定义和设计模式
- **ccc:delivery-core**: 代码生成器，根据设计模式生成组件代码

### 模式 2: Iteration Plan 实施

- **ccc:planner-core**: 计划解析器，读取和解析迭代计划文档

### 调度策略

**串行执行**:
- 模式1: cmd-implement → ccc:blueprint-core → ccc:delivery-core → 生成组件代码
- 模式2: cmd-implement → ccc:planner-core → 执行变更步骤

**并行执行**: 无（代码生成和增量变更需按顺序执行）

**错误处理**: 任何步骤失败时支持回滚到上一个稳定状态

### Agent 输入输出

| Agent | 输入 | 输出 |
|-------|------|------|
| ccc:blueprint-core | Blueprint 文档路径 | 解析后的组件定义和依赖关系 |
| ccc:delivery-core | 组件定义 + 设计模式 | 生成的组件代码文件 |
| ccc:planner-core | 迭代计划文档路径 | 解析后的执行步骤和依赖关系 |

### 调用示例

**模式 1: Blueprint 实现**
```
用户: /cmd-implement --blueprint=docs/designs/BLP-001-review-system.md
  ↓
cmd-implement 读取 Blueprint 文档
  ↓
调用 ccc:blueprint-core (解析组件定义)
  ↓
调用 ccc:delivery-core (生成代码)
  ↓
创建组件文件:
  Step 1: 创建目录结构
  Step 2: 生成 Skill 文件
  Step 3: 生成 SubAgent 文件
  Step 4: 生成 Hook 文件
  Step 5: 生成配置文件
  ↓
cmd-implement 生成实施报告
```

**模式 2: Iteration Plan 实施**
```
用户: /cmd-implement --plan=docs/designs/ITER-001-refactor.md
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

### 模式 1: 从 Blueprint 首次实现（正常设计流程）

```bash
# 从 Blueprint 实现完整组件
/cmd-implement --blueprint=docs/designs/BLP-001-my-component.md

# 分阶段实现
/cmd-implement --blueprint=docs/designs/BLP-001-my-component.md --phase=1

# 预览将要生成的代码
/cmd-implement --blueprint=docs/designs/BLP-001-my-component.md --dry-run
```

### 模式 2: 从 Iteration Plan 增量变更（迭代流程）

```bash
# 实施完整的迭代计划
/cmd-implement --plan=docs/designs/ITER-001-refactor.md

# 分阶段实施
/cmd-implement --plan=docs/designs/ITER-001-refactor.md --phase=1

# 预览变更
/cmd-implement --plan=docs/designs/ITER-001-refactor.md --dry-run
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--blueprint` | 模式1必需 | Path to Blueprint document (for initial implementation) |
| `--plan` | 模式2必需 | Path to iteration plan document (for incremental changes) |
| `--phase` | No | Specific phase number to implement |
| `--dry-run` | No | Preview changes without applying |

**注意**: `--blueprint` 和 `--plan` 互斥，必须且只能指定一个。

## Workflow

### 模式 1: Blueprint 首次实现

1. **Load Blueprint** - 解析 Blueprint 设计文档
2. **Extract Components** - 提取组件定义（Skill/SubAgent/Hook）
3. **Generate Code** - 根据设计模式生成代码框架
4. **Apply Details** - 填充业务逻辑和实现细节
5. **Verify** - 运行基础验证和测试
6. **Generate Report** - 创建实施报告

### 模式 2: Iteration Plan 增量变更

1. **Load Plan** - 解析迭代计划文档
2. **Validate Context** - 检查当前状态与计划假设一致
3. **Apply Changes** - 逐步执行修改
4. **Verify** - 运行测试和验证检查
5. **Generate Report** - 创建实施报告

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

### 模式 1: 从 Blueprint 实现

#### Example 1A: 实施完整的 Blueprint 设计

```bash
/cmd-implement --blueprint=docs/designs/BLP-001-review-system.md
```

**场景**: 根据 Blueprint 首次实现完整的审查系统组件

**输入**: Blueprint 包含以下组件定义
- cmd-review (Skill)
- review-core (SubAgent)
- review-aggregator (SubAgent)
- pre-review-check (Hook)

**执行过程**:
1. 解析 Blueprint 提取组件清单
2. 生成目录结构（skills/cmd-review/, agents/reviewer/等）
3. 根据设计模式生成每个组件的骨架代码
4. 填充业务逻辑（根据 Blueprint 的详细设计）
5. 创建配置文件和元数据
6. 运行基础验证测试

**输出文件**:
- 创建 4 个组件的完整代码（共 15 个文件）
- `docs/implementations/2026-03-15-review-system-impl.md`

**控制台输出**:
```
Implementation Complete: review-system

Components Created:
  ✓ skills/cmd-review/SKILL.md
  ✓ agents/reviewer/review-core/SKILL.md
  ✓ agents/reviewer/review-aggregator/SKILL.md
  ✓ hooks/pre-review-check.sh

Files Created: 15
Basic Tests: ✓ Passed

Implementation report: docs/implementations/2026-03-15-review-system-impl.md

Next Steps:
  1. Review generated code: /cmd-review --target=.
  2. Run full test suite
  3. Validate with /cmd-validate
```

#### Example 1B: 分阶段实施 Blueprint

```bash
/cmd-implement --blueprint=docs/designs/BLP-002-large-system.md --phase=1
```

**场景**: 大型系统分阶段实施，降低风险

**Blueprint 包含 4 个阶段**:
- Phase 1: 核心 Skill 和基础 SubAgent (2 个组件)
- Phase 2: 扩展 SubAgents (5 个组件)
- Phase 3: Hooks 和集成 (3 个组件)
- Phase 4: 文档和测试 (配套文件)

**输出**:
```
Implementation Complete: large-system (Phase 1/4)

Phase 1 Executed: Core Skills and Base SubAgents
Components Created: 2
Files Created: 8

Next: Run /cmd-implement --blueprint=docs/designs/BLP-002-large-system.md --phase=2
```

### 模式 2: 从 Iteration Plan 实施

#### Example 2A: 实施完整的重构计划

```bash
/cmd-implement --plan=docs/designs/component-extraction.md
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
/cmd-implement --plan=docs/designs/database-migration.md --phase=1
```

**场景**: 大型数据库迁移分阶段执行，避免风险

**用例**: 计划包含 5 个阶段，先执行第 1 阶段（添加新列），验证后再执行后续阶段

**输出**:
```
Implementation Complete: database-migration (Phase 1/5)

Phase 1 Executed: Add migration columns
Files Modified: 3
Tests Passed: ✓

Next: Run /cmd-implement --plan=docs/designs/database-migration.md --phase=2
```

### Example 3: 预览模式（Dry Run）

```bash
/cmd-implement --plan=docs/designs/api-refactor.md --dry-run
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
/cmd-implement --plan=docs/designs/multi-module-upgrade.md --phase=3
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
