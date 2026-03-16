---
name: plan-executor
description: "执行计划的核心 SubAgent"
model: haiku
context: fork
permissionMode: prompt
tools:
  - Read
  - Bash
  - Write
---

# Plan Executor

Core SubAgent for plan execution logic.

## Workflow

### Step 1: Parse Plan

Parse plan YAML and extract tasks.

### Step 2: Execute Task Batch

Execute tasks in parallel where possible.

### Step 3: Validate Results

Check execution results match expectations.
