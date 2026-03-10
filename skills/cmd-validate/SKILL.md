---
name: ccc:cmd-validate
model: sonnet
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
description: "Validates artifacts using external tools including YAML lint, schema validation, and token count analysis"
argument-hint: "[--artifact-id=current] [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:validate

Runs external validation (YAML lint, schema, token count).

## Usage

```bash
/ccc:validate --artifact-id=BLP-001
/ccc:validate --artifact-id=BLP-001 --lang=en-us
```

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |

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
