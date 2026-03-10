---
name: ccc:cmd-iterate
model: sonnet
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
description: "Iterates on existing blueprint artifacts to create improved versions with refinement tracking and change documentation"
argument-hint: "[--artifact-id=<id>] [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:iterate

Iterates on an existing blueprint artifact, creating a new version with improvements.

## Usage

```bash
/ccc:iterate --artifact-id=BLP-001
/ccc:iterate --artifact-id=BLP-001 --lang=en-us
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
- `/ccc:iterate --artifact-id=BLP-001` → `docs/iterations/2026-03-02-BLP-001-iteration.md`

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
/ccc:iterate --artifact-id=BLP-001
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
/ccc:iterate --artifact-id=BLP-003
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
/ccc:iterate --artifact-id=BLP-005 --lang=en-us
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
/ccc:iterate --artifact-id=BLP-008
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
/ccc:iterate --artifact-id=INT-001
```

**场景**: 尝试迭代 Intent 制品（不支持）

**输出**:
```
Error: Invalid artifact type for iteration

Artifact INT-001 is of type "Intent"
Only Blueprint artifacts support iteration.

Suggestion: Create a Blueprint first using /ccc:design
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
