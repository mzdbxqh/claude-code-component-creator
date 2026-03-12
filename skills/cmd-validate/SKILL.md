---
name: cmd-validate
model: sonnet
context: fork
disable-model-invocation: true
allowed-tools: [Read, Write, Edit, Glob, Grep]
description: "验证制品语法、Schema和Token预算。触发：验证/检查/确认。输出验证报告。主工作流第5步。"
argument-hint: "[--artifact-id=current] [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:validate

**完整流程**: `init` → `design` → `review` → `fix` → **validate** → `build`

Validates artifacts using external tools including YAML lint, schema validation, and token count analysis.

## 模型要求

- **推荐**: Claude Sonnet 4.5+ (高效能,最佳性价比)
- **可用**: Claude Haiku 3.5+ (快速验证,适用于简单检查)
- **最小**: Claude Haiku 3.5+ (最低要求)

### 功能需求
- 需要支持 Tool Use (Read, Write, Edit, Glob, Grep)
- 需要支持 Bash 调用外部验证工具 (yamllint, schema validator)
- 建议上下文窗口 >= 100K tokens

## SubAgents 协作

本工作流使用以下 SubAgents 进行任务分解和串行执行：

### 核心 Agents
- **ccc:validator-core**: 验证核心，协调所有验证任务和生成验证报告

### 调度策略
- **串行执行**: cmd-validate → ccc:validator-core → 执行所有验证步骤
- **并行执行**: 无（验证步骤有依赖关系）
- **错误处理**:
  - YAML 语法错误时终止流程
  - Schema 验证失败时继续其他检查，最后汇总报告
  - Token 超限时仅警告，不终止流程

### Agent 输入输出
| Agent | 输入 | 输出 |
|-------|------|------|
| ccc:validator-core | 制品文件路径 + artifact-id | 验证报告（包含所有检查结果）|

### 调用示例
```
用户: /ccc:validate --artifact-id=BLP-001
  ↓
cmd-validate 定位制品文件
  ↓
调用 ccc:validator-core (执行所有验证):
  Step 1: 加载制品文件
  Step 2: YAML 语法验证 (yamllint)
  Step 3: Schema 符合性验证
  Step 4: Token 预算分析
  Step 5: 交叉引用检查
  Step 6: 生成验证报告
  ↓
cmd-validate 输出验证摘要
```

### 验证流程细节
```
validator-core 内部工作流:
├─ Phase 1: 文件加载
│   ├─ 定位制品文件 (docs/ccc/{intent|blueprint|delivery}/)
│   ├─ 解析 YAML 内容
│   └─ 确定制品类型
├─ Phase 2: 语法验证
│   ├─ 调用 yamllint (如可用)
│   ├─ 检查缩进和格式
│   └─ 定位错误位置
├─ Phase 3: Schema 验证
│   ├─ 加载对应的 Schema 定义
│   ├─ 验证必填字段
│   ├─ 检查字段类型
│   └─ 验证字段关系
├─ Phase 4: Token 分析
│   ├─ 统计 Token 数量
│   ├─ 分析 Token 分布
│   ├─ 对比预算限制
│   └─ 生成优化建议
└─ Phase 5: 引用检查
    ├─ 验证 intent_id 引用
    ├─ 检查 blueprint_id 链接
    ├─ 验证工具引用
    └─ 检查 skills 字段引用
```

## Usage

```bash
/ccc:validate --artifact-id=BLP-001
/ccc:validate --artifact-id=BLP-001 --lang=en-us
```

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |

## Workflow

### 输入要求
- **必需参数**: `--artifact-id=<id>` 待验证的制品 ID（支持 BLP、INT、DLV）
- **可选参数**: `--lang=zh-cn|en-us|ja-jp` 输出语言（默认 zh-cn）
- **前置条件**:
  - 目标制品文件必须存在于对应目录
  - 验证工具可选（如 yamllint），缺失时跳过对应检查

### 执行步骤

**Step 1: 加载制品文件**
- 根据 artifact-id 定位制品文件路径
- 读取制品内容（YAML 格式）
- 解析制品类型（Intent、Blueprint、Delivery）
- **错误处理**: 制品不存在时列出可用制品供选择；artifact-id 格式无效时提示正确格式

**Step 2: YAML 语法验证**
- 使用 yamllint（如可用）检查语法
- 检测缩进错误、非法字符、格式问题
- 定位具体错误行号和列号
- **错误处理**: yamllint 不可用时跳过此检查并记录警告；语法错误时显示错误位置和修复建议

**Step 3: Schema 符合性验证**
- 加载对应制品类型的 Schema 定义
- 验证必填字段完整性
- 检查字段类型和值合法性
- 验证字段关系和依赖规则
- **错误处理**: Schema 文件缺失时使用内置规则验证；验证失败时列出所有不符合项

**Step 4: Token 预算分析**
- 统计制品总 Token 数量
- 分析各部分 Token 分布（metadata、workflow、tools 等）
- 对比预算限制（如 Blueprint 限制 4000 tokens）
- 计算使用率和剩余空间
- **错误处理**: Token 超限时提供优化建议（简化步骤、拆分组件）

**Step 5: 交叉引用检查**
- 验证 intent_id 引用的制品存在性
- 检查 blueprint_id 链接完整性
- 验证工具引用的有效性
- **错误处理**: 引用缺失时标记为警告而非错误；允许部分引用无效

**Step 6: 生成验证报告**
- 汇总所有验证结果
- 计算综合通过状态
- 生成详细报告文件
- 输出控制台摘要
- **错误处理**: 报告写入失败时输出到控制台；目录不存在时自动创建

### 预期输出
- **主要制品**: `docs/validations/YYYY-MM-DD-<artifact-id>-validation.md`
- **验证报告结构**:
  - 概览（制品 ID、验证日期、整体状态）
  - YAML 验证结果（语法检查通过/失败）
  - Schema 符合性（字段完整性、类型正确性）
  - Token 预算分析（使用率、分布图）
  - 交叉引用检查（引用完整性）
  - 质量评估（可选，针对 Intent/Blueprint）
  - 改进建议（问题修复指导）
- **控制台输出**: 简化的验证摘要，显示通过/失败状态和关键指标

### 错误处理
- **制品不存在** → 列出可用制品并提示使用 `/ccc:status` 查看所有制品
- **YAML 语法错误** → 显示错误行号、列号和具体问题，提供修复建议
- **Schema 验证失败** → 列出所有不符合项，标注优先级（P0 错误、P1 警告）
- **Token 超限** → 提供详细 Token 分布，建议使用 `/ccc:iterate` 优化
- **外部工具不可用** → 跳过该检查，标记为"部分验证"，建议安装缺失工具
- **通用错误** → 显示已完成的检查结果，标记未完成项，保存部分报告

## Output Specification

### Console Output

```
Validation Report: BLP-001

✓ YAML syntax valid
✓ Schema compliant
✓ Token budget: 2,456 / 4,000
✓ All required fields present
✓ Cross-references valid

Status: PASSED
```

### File Output

| Attribute | Value |
|-----------|-------|
| **Directory** | `docs/validations/` |
| **Filename** | `YYYY-MM-DD-<artifact-id>-validation.md` |
| **Format** | Markdown |
| **Overwrite** | No (timestamp ensures uniqueness) |

**Example:**
- `/ccc:validate --artifact-id=BLP-001` → `docs/validations/2026-03-02-BLP-001-validation.md`

### Report Structure

| Section | Content |
|---------|---------|
| Overview | Artifact validated, validation date |
| YAML Validation | Syntax check results |
| Schema Compliance | Schema validation results |
| Token Budget | Token count and limit |
| Cross-References | Reference integrity check |
| Summary | Overall status and issues |

## Examples

### Example 1: 验证 Blueprint 制品

```bash
/ccc:validate --artifact-id=BLP-001
```

**场景**: 验证新创建的 Blueprint 是否符合所有规范

**执行过程**:
1. 检查 YAML 语法
2. 验证 Schema 符合性
3. 计算 Token 预算
4. 检查交叉引用完整性
5. 生成验证报告

**输出**:
```
Validation Report: BLP-001

✓ YAML syntax valid
✓ Schema compliant (Blueprint v3.0)
✓ Token budget: 2,456 / 4,000 (61% used)
✓ All required fields present
  - artifact.id: BLP-001
  - metadata.name: deploy-skill
  - workflow.steps: 5 defined
  - tools: 3 tools selected
✓ Cross-references valid
  - intent_id: INT-001 [found]
  - All tool references valid

Status: ✅ PASSED (6/6 checks)

Validation report: docs/validations/2026-03-10-BLP-001-validation.md
```

### Example 2: 验证失败（YAML 语法错误）

```bash
/ccc:validate --artifact-id=BLP-005
```

**场景**: YAML 文件包含语法错误

**输出**:
```
Validation Report: BLP-005

✗ YAML syntax error
  Line 23: Invalid indentation
  Expected 2 spaces, found 3 spaces

  22 | workflow:
  23 |    steps:
         ^^^
  24 |   - name: analyze

Suggestion: Fix indentation to 2 spaces

✓ Schema validation: skipped (syntax error)
✓ Token budget: skipped (syntax error)
✗ Required fields: unable to verify
✗ Cross-references: unable to verify

Status: ❌ FAILED (1/5 checks passed)

Fix the YAML syntax and run validation again.
```

### Example 3: Token 预算超限警告

```bash
/ccc:validate --artifact-id=BLP-008
```

**场景**: 制品过于复杂，超出 Token 限制

**输出**:
```
Validation Report: BLP-008

✓ YAML syntax valid
✓ Schema compliant
⚠ Token budget: 4,523 / 4,000 (113% used) ⚠ EXCEEDED

Token breakdown:
  - Metadata: 245 tokens
  - Workflow: 2,890 tokens (65%)
  - Tool config: 987 tokens (22%)
  - Evidence chain: 401 tokens (9%)

✓ All required fields present
✓ Cross-references valid

Status: ⚠ WARNING (5/6 checks passed)

Recommendation:
  1. Simplify workflow (currently 12 steps)
  2. Consider splitting into multiple skills
  3. Reduce tool configuration verbosity

Run /ccc:iterate --artifact-id=BLP-008 to optimize
```

### Example 4: Schema 不符合（缺少必填字段）

```bash
/ccc:validate --artifact-id=BLP-010
```

**场景**: 制品缺少必填字段

**输出**:
```
Validation Report: BLP-010

✓ YAML syntax valid
✗ Schema validation failed

Missing required fields:
  - workflow.steps[0].error_handling (required)
  - metadata.creation_date (required)
  - tools[1].rationale (required)

Invalid field values:
  - artifact.version: "2.5" (must be "3.0")
  - workflow.complexity: "ultra" (allowed: simple, moderate, complex)

✓ Token budget: 1,890 / 4,000
✗ Required fields: 3 missing
⚠ Cross-references: 1 warning
  - intent_id: INT-999 not found (may have been deleted)

Status: ❌ FAILED (2/6 checks passed)

Fix schema violations:
  1. Add missing required fields
  2. Update artifact.version to "3.0"
  3. Change workflow.complexity to valid value
```

### Example 5: 验证 Intent 制品（多语言）

```bash
/ccc:validate --artifact-id=INT-003 --lang=en-us
```

**场景**: 验证英文输出的 Intent 制品

**输出**:
```
Validation Report: INT-003

✓ YAML syntax valid
✓ Schema compliant (Intent v3.0)
✓ Token budget: 856 / 2,000 (43% used)
✓ All required fields present
✓ Cross-references: N/A (Intent has no references)

Quality assessment:
  - Requirement clarity: High
  - Constraint completeness: Medium (consider adding more hard constraints)
  - Decision rationale: High

Status: ✅ PASSED (5/5 checks)

Suggestions for improvement:
  - Add 2-3 more hard constraints for better design guidance
  - Consider specifying performance requirements

Validation report: docs/validations/2026-03-10-INT-003-validation.md
```

### Example 6: 外部工具不可用

```bash
/ccc:validate --artifact-id=BLP-012
```

**场景**: YAML 验证工具未安装

**输出**:
```
Validation Report: BLP-012

⚠ YAML syntax validation: skipped (yamllint not installed)
  Suggestion: Install with 'pip install yamllint'

✓ Schema compliant (manual verification)
✓ Token budget: 2,105 / 4,000
✓ All required fields present
✓ Cross-references valid

Status: ⚠ PARTIAL (4/5 checks completed, 1 skipped)

Note: Install missing tools for complete validation
```

### Example 7: 验证 Delivery 制品（检查文件完整性）

```bash
/ccc:validate --artifact-id=DLV-001
```

**输出**:
```
Validation Report: DLV-001

✓ Delivery structure valid
✓ Required files present:
  - SKILL.md (178 lines)
  - README.md (45 lines)
  - metadata.yaml (valid)
  - tests/evals.json (valid)

✓ SKILL.md structure:
  - Frontmatter: valid YAML
  - Required sections: all present
  - Code examples: 3 found

✓ Cross-references:
  - blueprint_id: BLP-001 [found]
  - intent_id: INT-001 [found]

✓ Compliance score: 88/100

Status: ✅ PASSED (5/5 checks)

Validation report: docs/validations/2026-03-10-DLV-001-validation.md
```

## Error Handling

| Error Scenario | Handling Strategy |
|----------------|-------------------|
| Artifact not found | Display available artifacts for selection |
| YAML syntax error | Display error with line number and suggestion |
| Schema validation failure | List specific violations with fix suggestions |
| External tool unavailable | Skip that check, note in report |
| Token limit exceeded | Warn and suggest splitting component |

### File Access

```bash
# View the generated report
cat docs/validations/YYYY-MM-DD-<artifact-id>-validation.md

# List all validation reports
ls -la docs/validations/
```
