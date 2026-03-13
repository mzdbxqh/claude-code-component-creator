---
name: cmd-review
description: "Review execution results with quality checks. Triggers: review/检查/quality check"
model: sonnet
context: fork
tools:
  - Read
  - Grep
agents:
  - plan-executor
---

# Execution Review

Comprehensive review of execution results.

## Workflow

### Step 1: Load Results

Read execution results and artifacts.

### Step 2: Run Quality Checks

Execute 10+ quality checks across 3 dimensions.

### Step 3: Generate Report

Create review report with recommendations.
