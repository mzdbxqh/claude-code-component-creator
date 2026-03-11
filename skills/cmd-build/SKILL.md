---
name: ccc:cmd-build
model: sonnet
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
description: "构建交付 | 场景: 主工作流的终点"
argument-hint: "--artifact-id=<blueprint-id> [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:build

**完整流程**: `init` → `design` → `review` → `fix` → `validate` → **build**

Generates complete production-ready deliverable packages from validated blueprints including SKILL.md, implementation code, tests, and documentation.

## Usage

```bash
/ccc:build --artifact-id=BLP-001
/ccc:build --artifact-id=BLP-001 --lang=en-us
```

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |

## Workflow

### Step 1: Load Blueprint
**目标**: 读取并解析蓝图文件
**操作**: 从 docs/ccc/blueprint/ 加载指定的 BLP 文件
**输出**: 解析后的蓝图数据结构
**错误处理**: 蓝图文件不存在时列出可用蓝图并建议选择；蓝图格式无效时显示具体的解析错误位置

### Step 2: Generate SKILL.md
**目标**: 生成技能定义文件
**操作**: 根据蓝图生成 SKILL.md 文件
**输出**: SKILL.md 文件
**错误处理**: 模板缺失时使用默认模板并记录警告；生成失败时显示错误详情并跳过该文件继续执行

### Step 3: Generate Implementation
**目标**: 生成实现代码文件
**操作**: 根据蓝图规范创建代码文件
**输出**: implementation/ 目录下的代码文件
**错误处理**: 代码生成失败时记录具体文件错误并继续生成其他文件；目录创建失败时显示权限错误并终止

### Step 4: Generate Tests
**目标**: 生成测试文件
**操作**: 创建测试文件和夹具
**输出**: tests/ 目录下的测试文件
**错误处理**: 测试生成失败时记录警告并继续；缺少测试模板时创建基础测试框架

### Step 5: Package Delivery
**目标**: 创建交付物制品
**操作**: 打包所有生成的文件
**输出**: DLV 制品目录和构建报告
**错误处理**: 文件打包失败时回滚已创建文件并报告错误；部分文件缺失时标记为部分成功并生成不完整报告

## Output Specification

### Console Output

```
Build Complete: DLV-001

Files Generated: 5
  ✓ SKILL.md
  ✓ implementation/
  ✓ tests/
  ✓ README.md
  ✓ metadata.yaml

Status: SUCCESS

Build report: docs/ccc/delivery/2026-03-02-DLV-001/build-report.md
```

### File Output (Build Report)

| Attribute | Value |
|-----------|-------|
| **Directory** | `docs/ccc/delivery/YYYY-MM-DD-<artifact-id>/` |
| **Filename** | `build-report.md` |
| **Format** | Markdown |
| **Overwrite** | Yes (updated on rebuild) |

**Example:**
- `/ccc:build --artifact-id=BLP-001` → `docs/ccc/delivery/2026-03-02-DLV-001/build-report.md`

### Artifact Output (Delivery)

| Attribute | Value |
|-----------|-------|
| **Directory** | `docs/ccc/delivery/YYYY-MM-DD-<artifact-id>/` |
| **Contents** | Generated files (SKILL.md, implementation/, tests/, etc.) |
| **Format** | Mixed (Markdown, YAML, code files) |

### Build Report Structure

| Section | Content |
|---------|---------|
| Overview | Blueprint built, build date, delivery artifact ID |
| Build Status | Success/failure with details |
| Files Generated | List of created files |
| Verification Results | Tests passed, validation status |
| Source Blueprint | Reference to BLP artifact |
| Summary | Status and deployment readiness |

## Examples

### Example 1: Build a Simple Skill

```bash
/ccc:build --artifact-id=BLP-001
```

**Input**: Blueprint for a documentation reader skill

**Generated Output**:
```
docs/ccc/delivery/2026-03-02-DLV-001/
├── build-report.md
├── SKILL.md
├── metadata.yaml
├── README.md
└── implementation/
    └── (empty for pure skills)
```

**Console Output**:
```
Build Complete: DLV-001

Files Generated: 5
  ✓ SKILL.md
  ✓ implementation/
  ✓ tests/
  ✓ README.md
  ✓ metadata.yaml

Status: SUCCESS
Build report: docs/ccc/delivery/2026-03-02-DLV-001/build-report.md
```

### Example 2: Build Complex Multi-Component System

```bash
/ccc:build --artifact-id=BLP-005
```

**Input**: Blueprint with 3 subagents and 2 commands

**Generated Output**:
```
docs/ccc/delivery/2026-03-02-DLV-005/
├── build-report.md
├── README.md
├── agents/
│   ├── data-processor/SKILL.md
│   ├── validator/SKILL.md
│   └── reporter/SKILL.md
├── commands/
│   ├── process-data.md
│   └── generate-report.md
└── tests/
    ├── unit/
    └── integration/
```

### Example 3: Rebuild After Design Update

```bash
# Original build
/ccc:build --artifact-id=BLP-003

# Designer updates blueprint
/ccc:design --name=updated-skill --intent-id=INT-001

# Rebuild with same blueprint ID (overwrites delivery)
/ccc:build --artifact-id=BLP-003
```

## Error Handling

| Error Scenario | Handling Strategy |
|----------------|-------------------|
| Blueprint not found | Display available blueprints and suggest selection |
| Invalid blueprint ID | Display error with correct format example |
| File generation fails | Display specific file error and continue |
| Directory creation fails | Display permissions error |

### File Access

```bash
# View the build report
cat docs/ccc/delivery/YYYY-MM-DD-<artifact-id>/build-report.md

# List delivery files
ls -la docs/ccc/delivery/YYYY-MM-DD-<artifact-id>/

# View generated SKILL.md
cat docs/ccc/delivery/YYYY-MM-DD-<artifact-id>/SKILL.md
```
