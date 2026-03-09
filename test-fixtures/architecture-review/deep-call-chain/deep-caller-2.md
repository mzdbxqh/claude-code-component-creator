---
name: deep-caller-2
description: "Second level caller in deep call chain test"
context: fork
model: sonnet
allowed-tools:
  - Task
---

# Deep Caller 2

This skill calls deep-caller-3.

## Workflow

1. Call deep-caller-3
2. Process results

## Subagent Calls

- deep-caller-3 (Task)
