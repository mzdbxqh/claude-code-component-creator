---
name: component-c
description: "Component C in circular dependency test - calls Component A (creating cycle)"
context: fork
model: sonnet
allowed-tools:
  - Task
---

# Component C

This component calls Component A, completing the circular dependency.

## Workflow

1. Call component-a
2. Process results

## Subagent Calls

- component-a (Task)
