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

**Markdown报告完整结构**:

```markdown
# 验证报告：<Artifact-ID>

**验证时间**: 2026-03-10T15:30:00Z
**制品类型**: Blueprint
**Schema版本**: 3.0
**验证状态**: ✅ PASSED | ❌ FAILED | ⚠️ WARNING

---

## 1. YAML语法验证

**状态**: ✅ 通过 / ❌ 失败

- [x] YAML解析成功
- [x] 缩进格式正确
- [x] 特殊字符转义正确
- [x] 无语法错误

**错误详情**（如果有）:
```yaml
Line 45: unexpected indentation
Line 67: unquoted special character '@'
```

---

## 2. Schema合规性验证

**状态**: ✅ 通过 / ❌ 失败

**必需字段检查**:
- [x] artifact.version: "3.0" ✓
- [x] artifact.id: "BLP-001" ✓
- [x] artifact.type: "blueprint" ✓
- [x] metadata.name: "deploy-skill" ✓
- [x] workflow.steps: 5 个步骤 ✓
- [x] components: 3 个组件 ✓

**可选字段检查**:
- [x] metadata.description: 已提供 ✓
- [x] constraints: 已定义 ✓
- [ ] test_plan: 未提供 (建议补充)

**字段类型验证**:
- [x] version: string ✓
- [x] created_at: ISO8601 datetime ✓
- [x] quality.score: integer (0-100) ✓

---

## 3. Token预算验证

**状态**: ✅ 通过 / ⚠️ 警告 / ❌ 超预算

| 分类 | Token数 | 预算 | 使用率 |
|------|---------|------|--------|
| Skill内容 | 1,245 | 2,000 | 62% ✓ |
| Agent提示词 | 856 | 1,500 | 57% ✓ |
| 示例代码 | 355 | 500 | 71% ✓ |
| **总计** | **2,456** | **4,000** | **61%** ✓ |

**建议**:
- ✓ Token使用合理
- ⚠️ Agent提示词略长，建议优化
- ✓ 预留空间充足（39%）

---

## 4. 交叉引用验证

**状态**: ✅ 通过 / ❌ 失败

**引用完整性检查**:
- [x] intent_id: INT-001
  - 文件: docs/ccc/intent/2026-03-07-INT-001.yaml
  - 状态: ✅ 存在
- [x] 依赖组件引用
  - review-core: agents/reviewer/review-core/
  - 状态: ✅ 存在
- [x] 工具权限声明
  - allowed-tools: [Bash, Read, Write]
  - 状态: ✅ 合法

**引用错误**（如果有）:
```
❌ intent_id: INT-999 - 文件不存在
⚠️ component: missing-agent - 路径未找到
```

---

## 5. 能力表验证

**状态**: ✅ 通过 / ⚠️ 警告

| 维度 | 检查项 | 状态 |
|------|--------|------|
| 功能完整性 | 所有需求覆盖 | ✅ 100% |
| 工作流连贯性 | 步骤逻辑流畅 | ✅ 通过 |
| 工具权限 | 最小权限原则 | ✅ 合规 |
| 错误处理 | 异常场景覆盖 | ⚠️ 部分覆盖 |
| 测试计划 | 测试用例定义 | ❌ 缺失 |

**警告和建议**:
- ⚠️ 错误处理: 建议补充边界情况处理
- ❌ 测试计划: 强烈建议添加测试用例

---

## 6. 质量评分验证

**综合评分**: 87/100 (良好 B+)

| 维度 | 得分 | 说明 |
|------|------|------|
| 完整性 | 92/100 | 所有必需字段完整 |
| 清晰度 | 88/100 | 描述清晰，易理解 |
| 可行性 | 90/100 | 技术方案可行 |
| 可测试性 | 75/100 | 缺少测试计划（扣分） |

**质量建议**:
1. 补充测试计划 → 可测试性可提升至 90+
2. 优化Agent提示词 → Token使用更高效
3. 增强错误处理 → 鲁棒性更好

---

## 7. 验证总结

**总体状态**: ✅ 验证通过（允许build）

**检查摘要**:
- ✅ YAML语法: 通过
- ✅ Schema合规: 通过
- ✅ Token预算: 通过（61%使用率）
- ✅ 交叉引用: 通过
- ⚠️ 能力表: 通过（有警告）
- ✅ 质量评分: 87/100（良好）

**发现问题**:
- ❌ 0 个ERROR（阻断性）
- ⚠️ 2 个WARNING（建议修复）
- ℹ️ 3 个INFO（可选优化）

**下一步建议**:
- ✅ 可以继续执行 `/ccc:build`
- ⚠️ 建议先修复 WARNING 问题
- ℹ️ 可选：补充测试计划后质量更高

---

**验证报告生成时间**: 2026-03-10T15:30:00Z
**验证工具版本**: CCC v3.1.0
```

**YAML数据格式**（机器可读）:

```yaml
validation_report:
  artifact_id: "BLP-001"
  validated_at: "2026-03-10T15:30:00Z"
  artifact_type: "blueprint"
  schema_version: "3.0"
  overall_status: "PASSED"  # PASSED | FAILED | WARNING

  checks:
    yaml_syntax:
      status: "PASSED"
      errors: []
      warnings: []

    schema_compliance:
      status: "PASSED"
      required_fields_present: true
      required_fields:
        - field: "artifact.id"
          value: "BLP-001"
          status: "PASSED"
        - field: "metadata.name"
          value: "deploy-skill"
          status: "PASSED"
      optional_fields:
        - field: "test_plan"
          provided: false
          severity: "INFO"

    token_budget:
      status: "PASSED"
      total_tokens: 2456
      budget: 4000
      usage_percent: 61.4
      breakdown:
        skills: 1245
        agents: 856
        examples: 355
      warnings: []

    cross_references:
      status: "PASSED"
      references:
        - type: "intent"
          id: "INT-001"
          file: "docs/ccc/intent/2026-03-07-INT-001.yaml"
          status: "FOUND"
        - type: "component"
          id: "review-core"
          path: "agents/reviewer/review-core/"
          status: "FOUND"
      errors: []

    capability_matrix:
      status: "WARNING"
      dimensions:
        - name: "功能完整性"
          score: 100
          status: "PASSED"
        - name: "错误处理"
          score: 70
          status: "WARNING"
          message: "建议补充边界情况处理"
        - name: "测试计划"
          score: 0
          status: "FAILED"
          message: "缺少测试用例定义"

    quality_score:
      overall: 87
      dimensions:
        completeness: 92
        clarity: 88
        feasibility: 90
        testability: 75

  summary:
    total_checks: 6
    passed: 5
    failed: 0
    warnings: 1
    errors: 0
    warnings_list:
      - code: "WARN-001"
        severity: "WARNING"
        message: "缺少测试计划"
        suggestion: "添加 test_plan 字段"

    next_steps:
      can_build: true
      recommendations:
        - "可以执行 /ccc:build"
        - "建议先补充测试计划"

  metadata:
    generated_at: "2026-03-10T15:30:00Z"
    generator: "CCC v3.1.0"
    report_file: "docs/validations/2026-03-10-BLP-001-validation.md"
```

**字段说明**:

| Section | Field | Type | Description |
|---------|-------|------|-------------|
| validation_report | artifact_id | string | 被验证制品的ID |
| validation_report | validated_at | datetime | 验证时间（ISO8601） |
| validation_report | overall_status | enum | PASSED/FAILED/WARNING |
| checks | yaml_syntax | object | YAML语法检查结果 |
| checks | schema_compliance | object | Schema合规性检查 |
| checks | token_budget | object | Token预算检查 |
| checks | cross_references | object | 交叉引用验证 |
| checks | capability_matrix | object | 能力表检查 |
| checks | quality_score | object | 质量评分 |
| summary | can_build | boolean | 是否允许继续build |
| summary | recommendations | array | 改进建议列表 |

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
