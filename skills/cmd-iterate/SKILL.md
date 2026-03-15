---
name: cmd-iterate
model: sonnet
context: fork
disable-model-invocation: true
allowed-tools: [Read, Write, Edit, Glob, Grep]
description: "制品迭代流程第1步。迭代优化Blueprint，生成改进版本。触发：优化/简化/重构。自动检测改进机会，输出Blueprint-v2给review。"
argument-hint: "[--artifact-id=<id>] [--lang=zh-cn|en-us|ja-jp]"
---

# /cmd-iterate

**制品迭代流程**: Blueprint-v1 → **iterate** → Blueprint-v2 → `review` → `build`

Iterates on existing blueprint artifacts to create improved versions with refinement tracking and change documentation.

## 模型要求

- **推荐**: Claude Sonnet 4.5+ (高效能,最佳性价比)
- **可用**: Claude Opus 4.5+ (最高质量,深度优化)
- **最小**: Claude Sonnet 4.5+ (最低要求)

### 功能需求
- 需要支持 Tool Use (Read, Write, Edit, Glob, Grep)
- 需要支持多轮对话和设计优化
- 需要检测改进机会和生成优化方案
- 建议上下文窗口 >= 200K tokens (处理完整 Blueprint 迭代)

## SubAgents 协作

本工作流使用以下 SubAgents 进行任务执行：

### 核心 Agents
- **ccc:blueprint-core**: Blueprint 解析器，读取和分析现有 Blueprint 制品
- **ccc:architect-core**: 架构优化器，识别改进机会并生成优化方案

### 调度策略
- **串行执行**: cmd-iterate → ccc:blueprint-core → ccc:architect-core → 生成新版本 Blueprint
- **并行执行**: 无（迭代流程需按顺序执行）
- **错误处理**: 制品不存在时列出可用制品；未检测到改进点时报告"无需修改"

### Agent 输入输出
| Agent | 输入 | 输出 |
|-------|------|------|
| ccc:blueprint-core | Blueprint 制品路径 | 解析后的数据结构 |
| ccc:architect-core | 现有 Blueprint + 改进目标 | 优化后的 Blueprint 数据 |

### 调用示例
```
用户: /cmd-iterate --artifact-id=BLP-001
  ↓
cmd-iterate 读取现有 Blueprint
  ↓
调用 ccc:blueprint-core (解析和分析)
  ↓
调用 ccc:architect-core (检测改进机会):
  - 工具冗余检测
  - 步骤重复检测
  - 缺失边界处理检测
  ↓
生成优化方案并创建新版本 Blueprint (BLP-002)
  ↓
cmd-iterate 输出迭代报告和新制品路径
```

## Usage

```bash
/cmd-iterate --artifact-id=BLP-001
/cmd-iterate --artifact-id=BLP-001 --lang=en-us
```

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |

## Workflow

### Step 1: Load Artifact
**目标**: 加载指定的制品
**操作**: 从 docs/ccc/blueprint/ 读取指定制品或使用上下文制品
**输出**: 制品数据结构
**错误处理**: 制品不存在时列出可用制品并建议选择；制品类型不支持迭代时提示仅支持 Blueprint 类型

### Step 2: Analyze Improvement Opportunities
**目标**: 分析改进机会
**操作**: 检测制品中的问题和优化点
**输出**: 改进建议列表
**错误处理**: 未检测到改进点时报告"无需修改"并优雅退出；分析超时时使用已收集的部分结果继续执行

### Step 3: Apply Refinements
**目标**: 应用改进方案
**操作**: 基于反馈或检测到的问题应用改进
**输出**: 修改后的制品数据
**错误处理**: 改进应用失败时回滚到原始版本并报告具体错误；部分改进失败时标记失败项并继续应用其他改进

### Step 4: Generate New Artifact
**目标**: 生成新的制品 ID
**操作**: 创建递增 ID 的新制品（例如 BLP-001 → BLP-002）
**输出**: 新的制品文件
**错误处理**: 文件生成失败时显示具体错误并回滚变更；ID 冲突时自动查找下一个可用 ID

### Step 5: Create Iteration Report
**目标**: 生成迭代报告
**操作**: 记录所有变更和改进依据
**输出**: 迭代报告文件
**错误处理**: 报告生成失败时显示警告但不影响制品生成；目录不存在时自动创建 docs/iterations/

## Output Specification

### Console Output

```
Iteration Complete: BLP-001 → BLP-002

Changes Applied:
  ✓ Updated workflow steps
  ✓ Added error handling
  ✓ Refined tool selection

New Artifact: BLP-002
Status: READY for build

Iteration report: docs/iterations/2026-03-02-BLP-001-iteration.md
```

### File Output

| Attribute | Value |
|-----------|-------|
| **Directory** | `docs/iterations/` |
| **Filename** | `YYYY-MM-DD-<artifact-id>-iteration.md` |
| **Format** | Markdown |
| **Overwrite** | No (timestamp ensures uniqueness) |

**Example:**
- `/cmd-iterate --artifact-id=BLP-001` → `docs/iterations/2026-03-02-BLP-001-iteration.md`

### Artifact Output

| Attribute | Value |
|-----------|-------|
| **Directory** | `docs/ccc/blueprint/` |
| **Filename** | `YYYY-MM-DD-<new-artifact-id>.yaml` |
| **Format** | YAML |

### Report Structure

| Section | Content |
|---------|---------|
| Overview | Source artifact, iteration date, new artifact ID |
| Changes | List of modifications made |
| Rationale | Why changes were needed |
| Previous Artifact | Reference to BLP-001 |
| New Artifact | Reference to BLP-002 |
| Summary | Status and next steps |

## Examples

### Example 1: 改进 Blueprint 的工具选择

```bash
/cmd-iterate --artifact-id=BLP-001
```

**场景**: 初始设计使用了过多工具，导致复杂度过高

**输入**: BLP-001 使用了 Read、Write、Edit、Bash、Grep 五个工具

**执行过程**:
1. 加载 BLP-001
2. 分析发现工具选择冗余（可用 Edit 代替 Write+Read）
3. 应用改进：简化为 Edit、Bash、Grep 三个工具
4. 生成 BLP-002
5. 创建迭代报告

**输出**:
```
Iteration Complete: BLP-001 → BLP-002

Changes Applied:
  ✓ Simplified tool selection (5 → 3 tools)
  ✓ Consolidated file operations
  ✓ Updated workflow steps

New Artifact: BLP-002
Status: READY for build

Quality improvement: 85/100 → 92/100
Iteration report: docs/iterations/2026-03-10-BLP-001-iteration.md
```

### Example 2: 增强错误处理

```bash
/cmd-iterate --artifact-id=BLP-003
```

**场景**: 初始设计缺少完善的错误处理和边界情况处理

**改进内容**:
- 添加文件不存在时的 fallback 策略
- 增加超时机制
- 补充异常场景的恢复逻辑

**输出**:
```
Iteration Complete: BLP-003 → BLP-004

Changes Applied:
  ✓ Added error handling for missing files
  ✓ Implemented timeout mechanism (30s)
  ✓ Added 3 fallback strategies
  ✓ Enhanced workflow robustness

New Artifact: BLP-004
Status: READY for build

Iteration report: docs/iterations/2026-03-10-BLP-003-iteration.md
```

### Example 3: 优化工作流程顺序

```bash
/cmd-iterate --artifact-id=BLP-005 --lang=en-us
```

**场景**: 工作流步骤顺序不合理，导致重复操作

**改进前**:
```
1. Read file
2. Process data
3. Read file again (for validation)
4. Write result
```

**改进后**:
```
1. Read file
2. Process data
3. Validate in-memory
4. Write result
```

**输出**:
```
Iteration Complete: BLP-005 → BLP-006

Changes Applied:
  ✓ Reordered workflow steps
  ✓ Eliminated redundant file read
  ✓ Added in-memory validation

Performance improvement: ~40% faster execution

New Artifact: BLP-006
Status: READY for build

Iteration report: docs/iterations/2026-03-10-BLP-005-iteration.md
```

### Example 4: 无需改进的情况

```bash
/cmd-iterate --artifact-id=BLP-008
```

**场景**: Blueprint 已经是最优设计

**输出**:
```
Iteration Analysis: BLP-008

No improvements detected. The artifact is already well-designed:
  ✓ Tool selection optimal
  ✓ Workflow efficient
  ✓ Error handling comprehensive
  ✓ Quality score: 95/100

Status: No changes needed
```

### Example 5: 处理不支持的制品类型

```bash
/cmd-iterate --artifact-id=INT-001
```

**场景**: 尝试迭代 Intent 制品（不支持）

**输出**:
```
Error: Invalid artifact type for iteration

Artifact INT-001 is of type "Intent"
Only Blueprint artifacts support iteration.

Suggestion: Create a Blueprint first using /cmd-design
```

## Error Handling

| Error Scenario | Handling Strategy |
|----------------|-------------------|
| Artifact not found | Display available artifacts and suggest selection |
| No improvements detected | Report "No changes needed" and exit gracefully |
| Invalid artifact type for iteration | Display supported types (only Blueprint) |
| File generation failure | Display specific error and rollback changes |
| Permission denied | Display helpful message about file permissions |

### File Access

```bash
# View the iteration report
cat docs/iterations/YYYY-MM-DD-<artifact-id>-iteration.md

# View the new blueprint artifact
cat docs/ccc/blueprint/YYYY-MM-DD-<new-artifact-id>.yaml

# List all iteration reports
ls -la docs/iterations/
```
