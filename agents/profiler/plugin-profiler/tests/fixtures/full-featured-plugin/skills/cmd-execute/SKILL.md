---
name: cmd-execute
description: "Execute plan with validation. Triggers: execute/run/implement"
model: sonnet
context: fork
permissionMode: prompt
tools:
  - Read
  - Bash
  - Write
skills:
  - std-validation
---

# Plan Execution

Execute plan step by step with validation checkpoints.

## Workflow

### Step 1: Load Plan

Read plan file and parse tasks.

### Step 2: Execute Tasks

Run each task with validation.

### Step 3: Report Results

Generate execution report.
