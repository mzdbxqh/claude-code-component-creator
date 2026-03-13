---
name: cmd-plan
description: "Create execution plan using planning framework. Triggers: plan/planning/create plan"
model: sonnet
context: fork
tools:
  - Read
  - Write
argument-hint: "[--output=<path>]"
---

# Plan Creation

Create detailed execution plan with task breakdown.

## Workflow

### Step 1: Gather Requirements

Read requirements and clarify with user.

### Step 2: Create Plan Document

Generate plan with tasks, dependencies, and timeline.

### Step 3: Save Plan

Save plan to specified output path.
