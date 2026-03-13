---
name: cmd-build
model: sonnet
context: fork
disable-model-invocation: true
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
description: "从Blueprint生成生产就绪交付物。触发：构建/生成/打包。输出完整Delivery制品。主工作流终点。"
argument-hint: "--artifact-id=<blueprint-id> [--lang=zh-cn|en-us|ja-jp]"
---

# /cmd-build

**完整流程**: `init` → `design` → `review` → `fix` → `validate` → **build**

Generates complete production-ready deliverable packages from validated blueprints including SKILL.md, implementation code, tests, and documentation.

## 模型要求

- **推荐**: Claude Sonnet 4.5+ (高效能,最佳性价比)
- **可用**: Claude Opus 4.5+ (最高质量,复杂代码生成)
- **最小**: Claude Sonnet 4.5+ (最低要求)

### 功能需求
- 需要支持 Tool Use (Bash, Read, Write, Edit, Glob, Grep)
- 需要支持多轮对话和代码生成
- 需要处理多文件生成和模板渲染
- 建议上下文窗口 >= 200K tokens (处理完整 Blueprint 和代码生成)

## SubAgents 协作

本工作流使用以下 SubAgents 进行任务分解和串行执行：

### 核心 Agents
- **ccc:blueprint-core**: Blueprint 解析器，读取和验证 Blueprint 制品
- **ccc:delivery-core**: 交付物生成核心，协调所有代码生成任务
- **ccc:checkpoint-core**: 检查点核心，在关键步骤验证生成结果

### 调度策略
- **串行执行**: cmd-build → ccc:blueprint-core → ccc:delivery-core → ccc:checkpoint-core
- **并行执行**: 无（按顺序生成文件）
- **错误处理**:
  - Blueprint 解析失败时终止流程
  - 单个文件生成失败时记录错误，继续生成其他文件
  - 关键文件（SKILL.md）生成失败时终止流程

### Agent 输入输出
| Agent | 输入 | 输出 |
|-------|------|------|
| ccc:blueprint-core | Blueprint YAML 文件路径 | 解析后的数据结构 |
| ccc:delivery-core | Blueprint 数据 + lang 参数 | 生成的所有文件 |
| ccc:checkpoint-core | 生成的文件列表 | 验证报告 |

### 调用示例
```
用户: /cmd-build --artifact-id=BLP-001
  ↓
cmd-build 定位 Blueprint 文件
  ↓
调用 ccc:blueprint-core (解析和验证 Blueprint)
  ↓
调用 ccc:delivery-core (生成所有交付物):
  Step 1: 生成 SKILL.md
  Step 2: 生成实现代码 (implementation/)
  Step 3: 生成测试文件 (tests/)
  Step 4: 生成文档 (README.md)
  Step 5: 生成元数据 (metadata.yaml)
  ↓
调用 ccc:checkpoint-core (验证生成结果)
  ↓
cmd-build 打包 Delivery 制品
  ↓
输出构建报告和制品路径
```

### 生成流程细节
```
delivery-core 内部工作流:
├─ Phase 1: SKILL.md 生成
│   ├─ 提取 frontmatter (name, model, context, tools, description)
│   ├─ 生成工作流章节
│   ├─ 生成参数说明
│   └─ 生成示例和错误处理
├─ Phase 2: 实现代码生成
│   ├─ 创建 implementation/ 目录
│   ├─ 根据工作流生成代码文件
│   └─ 添加代码注释和文档字符串
├─ Phase 3: 测试生成
│   ├─ 创建 tests/ 目录
│   ├─ 生成测试用例
│   └─ 创建测试夹具 (test-fixtures/)
├─ Phase 4: 文档生成
│   ├─ 生成 README.md
│   └─ 生成使用指南
└─ Phase 5: 元数据生成
    └─ 创建 metadata.yaml (包含版本、依赖等)
```

## Usage

```bash
/cmd-build --artifact-id=BLP-001
/cmd-build --artifact-id=BLP-001 --lang=en-us
```

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |

## Workflow

### 输入要求
- **必需参数**: `--artifact-id=<blueprint-id>` Blueprint 制品 ID
- **可选参数**: `--lang=zh-cn|en-us|ja-jp` 输出语言（默认 zh-cn）
- **前置条件**:
  - Blueprint 制品必须存在且已通过验证
  - 建议先执行 `/cmd-validate` 确保 Blueprint 质量

### 执行步骤

**Step 1: 加载 Blueprint**
- 从 docs/ccc/blueprint/ 读取指定 Blueprint 文件
- 解析 YAML 结构和组件定义
- 验证 Blueprint 完整性和合法性
- **错误处理**: Blueprint 不存在时列出可用蓝图供选择；格式无效时显示具体解析错误位置

**Step 2: 生成 SKILL.md**
- 根据 Blueprint 工作流生成技能定义
- 填充 frontmatter（name、model、tools、description）
- 生成使用说明和示例章节
- 创建参数文档和输出规范
- **错误处理**: 模板缺失时使用默认模板并记录警告；生成失败时显示错误详情并跳过该文件

**Step 3: 生成实现代码**
- 根据 Blueprint 规范创建实现文件
- 生成 implementation/ 目录结构
- 创建代码骨架和注释
- 实现核心逻辑（如适用）
- **错误处理**: 代码生成失败时记录具体文件错误并继续其他文件；目录创建失败时显示权限错误

**Step 4: 生成测试文件**
- 创建 tests/ 目录和测试框架
- 生成 evals.json 测试定义
- 创建测试夹具（test-fixtures/）
- 编写测试文档（tests/README.md）
- **错误处理**: 测试生成失败时记录警告并继续；缺少测试模板时创建基础测试框架

**Step 5: 打包交付物**
- 创建 Delivery 制品目录
- 生成 metadata.yaml 和 README.md
- 复制或生成所有必需文件
- 创建构建报告（build-report.md）
- 验证交付物完整性
- **错误处理**: 文件打包失败时回滚已创建文件并报告错误；部分文件缺失时标记为部分成功并生成不完整报告

### 预期输出
- **主要制品**: `docs/ccc/delivery/YYYY-MM-DD-<artifact-id>/`
- **交付物结构**:
  - SKILL.md（技能定义）
  - implementation/（实现代码）
  - tests/（测试文件和夹具）
  - README.md（使用说明）
  - metadata.yaml（元数据）
  - build-report.md（构建报告）
- **控制台输出**: Build Complete 摘要、生成文件列表、状态、报告路径

### 错误处理
- **Blueprint 不存在** → 列出可用 Blueprint 或建议先执行 `/cmd-design`
- **Blueprint ID 无效** → 显示正确格式示例（如 BLP-001）
- **文件生成失败** → 显示具体文件错误，继续生成其他文件
- **目录创建失败** → 显示权限错误并检查文件系统权限
- **通用错误** → 保存已生成的文件，提供清理或继续的命令

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
- `/cmd-build --artifact-id=BLP-001` → `docs/ccc/delivery/2026-03-02-DLV-001/build-report.md`

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
/cmd-build --artifact-id=BLP-001
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
/cmd-build --artifact-id=BLP-005
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
/cmd-build --artifact-id=BLP-003

# Designer updates blueprint
/cmd-design --name=updated-skill --intent-id=INT-001

# Rebuild with same blueprint ID (overwrites delivery)
/cmd-build --artifact-id=BLP-003
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
