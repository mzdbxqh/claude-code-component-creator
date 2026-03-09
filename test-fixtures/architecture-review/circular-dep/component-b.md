---
name: component-b
description: "Component B in circular dependency test - calls Component C"
context: fork
model: sonnet
allowed-tools:
  - Task
---

# Component B

This component calls Component C.

## Workflow

1. Call component-c
2. Process results

## Subagent Calls

- component-c (Task)
