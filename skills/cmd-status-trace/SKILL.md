---
name: ccc:status-trace
model: sonnet
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
description: "Displays traceability matrix showing requirement coverage from intent through blueprint to delivery with gap analysis and action items"
argument-hint: "[--project-id=current] [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:status-trace

Shows traceability matrix linking requirements to implementation.

## Usage

```bash
# Basic usage - show trace for current project
/ccc:status-trace

# Show trace for specific project
/ccc:status-trace --project-id=my-project

# Filter by requirement type
/ccc:status-trace --type=functional

# Show only untraced requirements
/ccc:status-trace --filter=untraced

# Export trace data to JSON
/ccc:status-trace --export=trace.json

# Show trace with coverage percentage
/ccc:status-trace --coverage

# Limit to specific requirement
/ccc:status-trace --requirement=REQ-001

# Show trace in English
/ccc:status-trace --lang=en-us
```

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |

## Examples

### Example 1: Full Traceability Matrix
```bash
/ccc:status-trace --project-id=payment-system
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
/ccc:status-trace --project-id=inventory --filter=missing
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
/ccc:status-trace --project-id=user-portal --coverage
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
- `/ccc:status-trace --project-id=payment-system` → `docs/traces/2026-03-02-payment-system-trace.md`

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
   → Ensure artifacts are properly linked with '/ccc:link'

❌ Error: Incomplete trace chain for requirement 'REQ-001'
   → Check links: Intent → Blueprint → Delivery

❌ Error: Traceability matrix generation failed
   → Run '/ccc:validate' to check project structure
```

### Recovery Steps

1. **Validate links**: `/ccc:validate --project-id=<id>`
2. **Check specific requirement**: `/ccc:trace --requirement=<req-id>`
3. **Export trace data**: `/ccc:status-trace --export=trace.json`
4. **Generate partial matrix**: `/ccc:status-trace --partial`
