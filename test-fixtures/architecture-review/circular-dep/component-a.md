---
name: component-a
description: "Component A in circular dependency test - calls Component B"
context: fork
model: sonnet
allowed-tools:
  - Task
---

# Component A

This component calls Component B, creating a circular dependency.

## Workflow

1. Call component-b
2. Process results

## Subagent Calls

- component-b (Task)
