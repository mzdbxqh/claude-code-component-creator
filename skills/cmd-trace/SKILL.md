---
name: ccc:cmd-trace
model: sonnet
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
description: "Generates comprehensive traceability matrix linking intent requirements to blueprint elements and delivery implementations with coverage analysis"
argument-hint: "<project-id> [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:trace

Generates full traceability matrix for the project.

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |

## Output Specification

### Console Output

```
Traceability Matrix: my-project

Intent Requirement          │ Blueprint Element      │ Delivery File:Line
────────────────────────────┼────────────────────────┼───────────────────
Auto-deploy                 │ deployment-workflow    │ deploy-skill.md:45
K8s support                 │ k8s-config             │ deploy-skill.md:67
Error handling              │ rollback-strategy      │ deploy-skill.md:89
GitOps workflow             │ git-trigger            │ deploy-skill.md:120

Coverage: 95% (19/20 requirements traced)
```

### File Output

| Attribute | Value |
|-----------|-------|
| **Directory** | `docs/traces/` |
| **Filename** | `YYYY-MM-DD-<project-id>-trace.md` |
| **Format** | Markdown |
| **Overwrite** | No (timestamp ensures uniqueness) |

**Example:**
- `/ccc:trace my-project` → `docs/traces/2026-03-02-my-project-trace.md`

### Report Structure

| Section | Content |
|---------|---------|
| Overview | Project traced, trace date |
| Traceability Matrix | Intent → Blueprint → Delivery mapping |
| Coverage Analysis | Percentage and gaps |
| Requirements | List of traced requirements |
| Gaps | Untraced or partially traced items |
| Summary | Overall coverage status |

## Workflow

### Step 1: Validate Project
**目标**: 验证项目存在性
**操作**: 检查项目 ID 是否有效
**输出**: 验证结果
**错误处理**: 项目不存在时使用 /ccc:projects 列出可用项目；项目 ID 格式无效时显示正确格式示例

### Step 2: Collect Traceable Artifacts
**目标**: 收集可追溯制品
**操作**: 扫描项目中的 Intent、Blueprint、Delivery
**输出**: 制品列表
**错误处理**: 无可追溯制品时提示使用 /ccc:init 创建制品并用 /ccc:link 建立链接；制品链接缺失时记录警告并继续处理其他制品

### Step 3: Generate Traceability Matrix
**目标**: 生成完整的可追溯性矩阵
**操作**: 映射需求到实现的完整链路
**输出**: 可追溯性矩阵
**错误处理**: 矩阵生成失败时显示错误并提供部分矩阵；需求映射不完整时标记缺口并在报告中突出显示

### Step 4: Analyze Coverage
**目标**: 分析覆盖率
**操作**: 计算追溯覆盖百分比和缺口
**输出**: 覆盖率分析报告
**错误处理**: 分析失败时使用基础统计并记录警告；数据不一致时进行数据清洗并标注可信度

### Step 5: Write Report
**目标**: 输出追溯报告
**操作**: 生成报告文件
**输出**: docs/traces/ 下的报告文件
**错误处理**: 输出目录缺失时自动创建 docs/traces/ 目录；文件写入权限被拒时显示权限错误并建议手动创建目录

### File Access

```bash
# View the generated report
cat docs/traces/YYYY-MM-DD-<project-id>-trace.md

# List all traceability reports
ls -la docs/traces/
```

## Error Handling

### Common Errors

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `TRACE-GEN-001` | Project not found | Verify project ID exists |
| `TRACE-GEN-002` | No traceable artifacts | Create artifacts with proper links |
| `TRACE-GEN-003` | Output directory missing | Create `docs/traces/` directory |
| `TRACE-GEN-004` | File write permission denied | Check directory permissions |

### Error Messages

```
❌ Error: Project 'invalid-project' not found
   → Use '/ccc:projects' to list available projects

❌ Error: No traceable artifacts in project 'my-project'
   → Create artifacts with '/ccc:init' and link with '/ccc:link'

❌ Error: Cannot create output directory 'docs/traces/'
   → Check permissions or create directory manually

❌ Error: Permission denied writing trace report
   → Check write permissions for 'docs/traces/' directory
```

### Recovery Steps

1. **Verify project**: `/ccc:projects`
2. **Check artifacts**: `/ccc:list --project-id=<id>`
3. **Create output directory**: `mkdir -p docs/traces/`
4. **Generate partial trace**: `/ccc:trace <project-id> --partial`
5. **Export to alternative location**: `/ccc:trace <project-id> --output=/tmp/trace.md`

## 使用示例 (Examples)

### Example 1: 基础追溯矩阵生成

```bash
/ccc:trace payment-system
```

**输入**: 支付系统项目 ID

**输出**:
```
Traceability Matrix: payment-system

Intent Requirement          │ Blueprint Element      │ Delivery File:Line
────────────────────────────┼────────────────────────┼───────────────────
Process credit card payment │ payment-processor      │ payment-skill.md:45
Handle refunds              │ refund-handler         │ refund-skill.md:67
Validate card details       │ card-validator         │ validation-skill.md:23
GitOps workflow             │ git-trigger            │ deploy-skill.md:120
Support multiple currencies │ currency-converter     │ currency-skill.md:34
Error handling & retry      │ error-handler          │ error-skill.md:78
Fraud detection             │ fraud-detector         │ fraud-skill.md:90
Webhook notifications       │ webhook-dispatcher     │ webhook-skill.md:56

Coverage: 100% (8/8 requirements traced)

Report saved to: docs/traces/2026-03-11-payment-system-trace.md
```

### Example 2: 多语言输出

```bash
/ccc:trace api-gateway --lang=en-us
```

**输入**: API 网关项目，英文输出

**输出**:
```
Traceability Matrix: api-gateway

Intent Requirement       │ Blueprint Element   │ Delivery File:Line
─────────────────────────┼─────────────────────┼────────────────────
Rate limiting            │ rate-limiter        │ limiter-skill.md:12
Authentication & Auth    │ auth-middleware     │ auth-skill.md:34
Request routing          │ router-config       │ router-skill.md:56
API versioning           │ version-handler     │ version-skill.md:23
Error handling           │ error-middleware    │ error-skill.md:45

Coverage: 100% (5/5 requirements traced)

Report saved to: docs/traces/2026-03-11-api-gateway-trace.md
```

### Example 3: 部分追溯场景（有缺口）

```bash
/ccc:trace microservices-platform
```

**输入**: 微服务平台项目（开发中，部分需求未完成）

**输出**:
```
Traceability Matrix: microservices-platform

Intent Requirement          │ Blueprint Element      │ Delivery File:Line
────────────────────────────┼────────────────────────┼───────────────────
Service discovery           │ discovery-service      │ discovery-skill.md:34
Load balancing              │ load-balancer          │ lb-skill.md:56
Circuit breaker             │ circuit-breaker        │ breaker-skill.md:78
Distributed tracing         │ tracing-integration    │ [MISSING]
Config management           │ config-server          │ config-skill.md:90
API gateway                 │ gateway-service        │ gateway-skill.md:123
Service mesh                │ [MISSING]              │ [MISSING]
Health monitoring           │ health-checker         │ [PARTIAL: health-skill.md:45]

Coverage: 62.5% (5/8 requirements traced)

Gaps Identified:
  ❌ "Distributed tracing" - Blueprint exists, no Delivery
  ❌ "Service mesh" - No Blueprint or Delivery
  ⚠️ "Health monitoring" - Delivery incomplete

Recommended Actions:
  1. Implement Delivery for "Distributed tracing" (Priority: High)
  2. Create Blueprint for "Service mesh" (Priority: Medium)
  3. Complete "Health monitoring" Delivery (Priority: Low)

Report saved to: docs/traces/2026-03-11-microservices-platform-trace.md
```

### Example 4: 大型项目追溯

```bash
/ccc:trace enterprise-erp
```

**输入**: 企业 ERP 系统（50+ 需求）

**输出**:
```
Traceability Matrix: enterprise-erp

Analyzing 52 requirements across 15 modules...

Intent Requirement            │ Blueprint Element        │ Delivery File:Line
──────────────────────────────┼──────────────────────────┼────────────────────
[Module: Finance]
  Invoice generation          │ invoice-generator        │ invoice-skill.md:23
  Payment processing          │ payment-processor        │ payment-skill.md:45
  Budget tracking             │ budget-tracker           │ budget-skill.md:67
  Financial reporting         │ report-generator         │ report-skill.md:89

[Module: Inventory]
  Stock management            │ stock-manager            │ stock-skill.md:34
  Warehouse operations        │ warehouse-controller     │ warehouse-skill.md:56
  Supplier integration        │ supplier-api             │ supplier-skill.md:78

[Module: HR]
  Employee management         │ employee-manager         │ employee-skill.md:45
  Payroll processing          │ payroll-processor        │ payroll-skill.md:67
  Attendance tracking         │ attendance-tracker       │ attendance-skill.md:89

... (showing 10/52 requirements, see full report for details)

Coverage Summary:
  ✓ Finance Module: 95% (19/20)
  ✓ Inventory Module: 100% (12/12)
  ⚠️ HR Module: 80% (8/10)
  ⚠️ Sales Module: 75% (6/8)
  ❌ CRM Module: 50% (1/2)

Overall Coverage: 88.5% (46/52 requirements traced)

Report saved to: docs/traces/2026-03-11-enterprise-erp-trace.md
(Full matrix with all 52 requirements available in report)
```

### Example 5: 错误场景 - 项目不存在

```bash
/ccc:trace non-existent-project
```

**输入**: 不存在的项目 ID

**输出**:
```
❌ Error: Project 'non-existent-project' not found
   → Use '/ccc:projects' to list available projects

Available Projects:
  1. payment-system
  2. api-gateway
  3. microservices-platform
  4. enterprise-erp

Suggestions:
  - Check project ID spelling
  - Run: /ccc:projects
  - Create new project: /ccc:init --project-id=your-project
```

### Example 6: 边界情况 - 无制品项目

```bash
/ccc:trace empty-project
```

**输入**: 已创建但无任何制品的项目

**输出**:
```
❌ Error: No traceable artifacts in project 'empty-project'
   → Create artifacts with '/ccc:init' and link with '/ccc:link'

Current Project Status:
  ✓ Project exists
  ❌ No Intent artifacts
  ❌ No Blueprint artifacts
  ❌ No Delivery artifacts

Getting Started:
  1. Create Intent: /ccc:init --type=intent --project-id=empty-project
  2. Create Blueprint: /ccc:design --intent-id=INT-001
  3. Create Delivery: /ccc:build --blueprint-id=BLP-001
  4. Generate trace: /ccc:trace empty-project

Alternative:
  - Import from template: /ccc:import --template=starter --project-id=empty-project
```
