---
name: deep-caller-3
description: "Third level caller in deep call chain test"
context: fork
model: sonnet
allowed-tools:
  - Task
---

# Deep Caller 3

This skill calls deep-caller-4.

## Workflow

1. Call deep-caller-4
2. Process results

## Subagent Calls

- deep-caller-4 (Task)
