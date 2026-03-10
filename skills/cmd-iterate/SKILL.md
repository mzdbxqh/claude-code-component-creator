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
