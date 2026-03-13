---
name: cmd-status-trace
model: sonnet
context: fork
disable-model-invocation: true
allowed-tools: [Read, Glob, Grep]
description: "显示需求覆盖的追溯矩阵。触发：追踪/覆盖率/缺口。输出映射表和覆盖率百分比。"
argument-hint: "[--project-id=current] [--lang=zh-cn|en-us|ja-jp]"
---

# /cmd-status-trace

Displays traceability matrix showing requirement coverage from intent through blueprint to delivery with gap analysis and action items.

## 模型要求

- **推荐**: Claude Sonnet 4.5+ (高效能,最佳性价比)
- **可用**: Claude Haiku 3.5+ (快速推理,适用于简单追溯)
- **最小**: Claude Haiku 3.5+ (最低要求)

### 功能需求
- 需要支持 Tool Use (Read, Glob, Grep)
- 需要支持多轮对话
- 建议上下文窗口 >= 100K tokens

## SubAgents 协作

本工作流使用以下 SubAgents 进行任务执行：

### 核心 Agents
本 skill 主要使用文件扫描和映射分析，不需要专门的 SubAgent。直接使用 Read, Glob, Grep 工具完成。

### 调度策略
- **串行执行**: cmd-status-trace → 扫描制品 → 构建追溯矩阵 → 分析覆盖率
- **并行执行**: 无（追溯分析为简单操作）
- **错误处理**: 制品缺失时标记为缺口；引用断裂时记录未覆盖项

### 调用示例
```
用户: /cmd-status-trace
  ↓
cmd-status-trace 扫描所有制品并构建追溯关系
  ↓
生成追溯矩阵:
  需求 1 → Blueprint 元素 A → Delivery 文件 X
  需求 2 → Blueprint 元素 B → (未实现)
  ↓
计算覆盖率: 85% (17/20)
  ↓
输出追溯报告
```

## Usage

```bash
# Basic usage - show trace for current project
/cmd-status-trace

# Show trace for specific project
/cmd-status-trace --project-id=my-project

# Filter by requirement type
/cmd-status-trace --type=functional

# Show only untraced requirements
/cmd-status-trace --filter=untraced

# Export trace data to JSON
/cmd-status-trace --export=trace.json

# Show trace with coverage percentage
/cmd-status-trace --coverage

# Limit to specific requirement
/cmd-status-trace --requirement=REQ-001

# Show trace in English
/cmd-status-trace --lang=en-us
```

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |

## Examples

### Example 1: Full Traceability Matrix
```bash
/cmd-status-trace --project-id=payment-system
```
```
Traceability Matrix: payment-system

Requirement (Intent)          │ Blueprint              │ Delivery              │ Status
──────────────────────────────┼────────────────────────┼───────────────────────┼─────────
Process credit card payment   │ payment-processor      │ payment-skill.md:45   │ ✓ Traced
Handle refunds               │ refund-handler         │ refund-skill.md:67    │ ✓ Traced
Validate card details        │ card-validator         │ validation-skill.md:23│ ⚠ Partial
Fraud detection              │ fraud-detector         │                       │ ❌ Missing

Coverage: 75% (3/4 requirements)
```

### Example 2: Filtered by Status
```bash
/cmd-status-trace --project-id=inventory --filter=missing
```
```
Missing Traces: inventory

Requirement                │ Gap Analysis
───────────────────────────┼────────────────────────────
Real-time stock updates    │ No Blueprint linked
Multi-warehouse support    │ Blueprint exists, no Delivery
Barcode scanning           │ Intent not created

Action Items:
1. Create Blueprint for "Real-time stock updates"
2. Implement Delivery for "Multi-warehouse support"
3. Create Intent for "Barcode scanning"
```

### Example 3: Coverage Report
```bash
/cmd-status-trace --project-id=user-portal --coverage
```
```
Coverage Report: user-portal

Total Requirements: 8
┌────────────────────┬───────┬──────────┐
│ Status             │ Count │ Percent  │
├────────────────────┼───────┼──────────┤
│ Fully Traced       │ 5     │ 62.5%    │
│ Partially Traced   │ 2     │ 25.0%    │
│ Not Traced         │ 1     │ 12.5%    │
└────────────────────┴───────┴──────────┘

Top Gaps:
1. "Social login integration" - Missing Delivery
2. "Profile customization" - Missing Blueprint
3. "Notification preferences" - Not started
```

### Example 4: 特定需求追溯

```bash
/cmd-status-trace --project-id=e-commerce --requirement=REQ-001
```

**输入**: 电商项目，追溯特定需求 REQ-001（购物车功能）

**输出**:
```
Traceability for Requirement: REQ-001 (Shopping Cart)

Intent: INT-005 (E-commerce Core)
   └─ Requirement: Shopping Cart Management
       │
       ▼
Blueprint: BLP-012 (Cart Service Design)
   ├─ Component: cart-state-manager
   ├─ Component: cart-persistence
   └─ Component: cart-api
       │
       ▼
Delivery: Multiple implementations
   ├─ DLV-023 (Cart State Manager) [completed] ✓
   │   └─ File: skills/cart/state-manager.md:34-89
   ├─ DLV-024 (Cart Persistence) [completed] ✓
   │   └─ File: skills/cart/persistence.md:12-67
   └─ DLV-025 (Cart API) [in_progress] ⏳
       └─ File: commands/cart-api.md:45-120

Trace Status: ⚠️ Partially Complete
   - Intent → Blueprint: ✓ Complete
   - Blueprint → Delivery: ⚠️ 2/3 components delivered

Next Action: Complete DLV-025 (Cart API) implementation

Report saved to: docs/traces/2026-03-11-REQ-001-trace.md
```

### Example 5: JSON 导出用于自动化

```bash
/cmd-status-trace --project-id=banking --export=trace.json --coverage
```

**输入**: 银行系统项目，导出 JSON 格式的追溯数据

**输出**:
- 控制台显示简要的覆盖率摘要
- 生成 `trace.json` 文件：
```json
{
  "project": "banking",
  "generatedAt": "2026-03-11T10:30:00Z",
  "coverage": {
    "total": 45,
    "fullyTraced": 38,
    "partiallyTraced": 5,
    "notTraced": 2,
    "percentage": 84.4
  },
  "traces": [
    {
      "requirement": "Account Management",
      "intentId": "INT-010",
      "blueprintId": "BLP-025",
      "deliveryIds": ["DLV-050", "DLV-051"],
      "status": "complete",
      "files": [
        "skills/account/manager.md:23",
        "skills/account/validator.md:45"
      ]
    }
  ],
  "gaps": [
    {
      "requirement": "Real-time Fraud Detection",
      "issue": "No Blueprint linked",
      "severity": "high"
    }
  ]
}
```
- 可用于 CI/CD 管道、质量门禁、自动化报告生成

### Example 6: 边界情况 - 无追溯数据

```bash
/cmd-status-trace --project-id=legacy-system
```

**输入**: 遗留系统项目（制品缺少链接信息）

**输出**:
```
❌ Error: No traceability data found for project 'legacy-system'
   → Ensure artifacts are properly linked with '# 手动链接工件 (功能计划中)'

Diagnostics:
   ✓ Found 5 Intent artifacts
   ✓ Found 8 Blueprint artifacts
   ✓ Found 12 Delivery artifacts
   ❌ No links between artifacts

Recovery Steps:
   1. Review artifacts: /cmd-status --project-id=legacy-system
   2. Link Intent to Blueprint: # 手动链接工件 (功能计划中) --from=INT-001 --to=BLP-001
   3. Link Blueprint to Delivery: # 手动链接工件 (功能计划中) --from=BLP-001 --to=DLV-001
   4. Retry trace: /cmd-status-trace --project-id=legacy-system

Alternative:
   - Generate partial matrix: /cmd-status-trace --partial
   - Export raw data: /cmd-status-trace --export=raw.json
```

## Output Specification

### Console Output

```
Traceability Matrix: payment-system

Requirement (Intent)          │ Blueprint              │ Delivery              │ Status
──────────────────────────────┼────────────────────────┼───────────────────────┼─────────
Process credit card payment   │ payment-processor      │ payment-skill.md:45   │ ✓ Traced
Handle refunds               │ refund-handler         │ refund-skill.md:67    │ ✓ Traced
Validate card details        │ card-validator         │ validation-skill.md:23│ ⚠ Partial
Fraud detection              │ fraud-detector         │                       │ ❌ Missing

Coverage: 75% (3/4 requirements)
```

### File Output

| Attribute | Value |
|-----------|-------|
| **Directory** | `docs/traces/` |
| **Filename** | `YYYY-MM-DD-<project-id>-trace.md` |
| **Format** | Markdown |
| **Overwrite** | No (timestamp ensures uniqueness) |

**Example:**
- `/cmd-status-trace --project-id=payment-system` → `docs/traces/2026-03-02-payment-system-trace.md`

### Export Options

| Option | Description |
|--------|-------------|
| `--export=json` | Export trace data as JSON |
| `--coverage` | Include coverage percentage report |
| `--filter=missing` | Show only untraced requirements |

### Report Structure

| Section | Content |
|---------|---------|
| Overview | Project name, trace date |
| Traceability Matrix | Intent → Blueprint → Delivery mapping |
| Coverage Analysis | Percentage and gap statistics |
| Action Items | Recommended fixes for gaps |

## Workflow

### Step 1: Load Project Artifacts
**目标**: 加载项目的所有制品
**操作**: 读取 Intent、Blueprint、Delivery 制品
**输出**: 制品数据集合
**错误处理**: 项目不存在时列出可用项目并建议选择；无制品时提示先创建制品

### Step 2: Build Traceability Matrix
**目标**: 构建可追溯性矩阵
**操作**: 映射 Intent → Blueprint → Delivery 链接
**输出**: 可追溯性矩阵数据
**错误处理**: 链接不完整时标记为"部分追溯"并在报告中注明缺失环节；链接信息缺失时尝试自动推断并标记为"推断"

### Step 3: Calculate Coverage
**目标**: 计算覆盖率
**操作**: 统计已追溯和未追溯需求
**输出**: 覆盖率百分比和缺口分析
**错误处理**: 统计数据不一致时记录警告并使用保守估算；无法计算覆盖率时显示原始追溯数据

### Step 4: Generate Report
**目标**: 生成追溯报告
**操作**: 输出矩阵、覆盖率和行动项
**输出**: 追溯报告文件
**错误处理**: 报告生成失败时显示到控制台并提示文件权限问题；目录不存在时自动创建 docs/traces/

### File Access

```bash
# View the generated trace report
cat docs/traces/YYYY-MM-DD-<project-id>-trace.md

# List all trace reports
ls -la docs/traces/
```

## Error Handling

### Common Errors

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `TRACE-001` | No traceability data | Ensure artifacts have proper links |
| `TRACE-002` | Incomplete trace chain | Check Intent→Blueprint→Delivery links |
| `TRACE-003` | Matrix generation failed | Verify project structure integrity |

### Error Messages

```
❌ Error: No traceability data found for project 'my-project'
   → Ensure artifacts are properly linked with '# 手动链接工件 (功能计划中)'

❌ Error: Incomplete trace chain for requirement 'REQ-001'
   → Check links: Intent → Blueprint → Delivery

❌ Error: Traceability matrix generation failed
   → Run '/cmd-validate' to check project structure
```

### Recovery Steps

1. **Validate links**: `/cmd-validate --project-id=<id>`
2. **Check specific requirement**: `/cmd-trace --requirement=<req-id>`
3. **Export trace data**: `/cmd-status-trace --export=trace.json`
4. **Generate partial matrix**: `/cmd-status-trace --partial`
