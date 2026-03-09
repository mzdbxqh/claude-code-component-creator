---
name: deep-caller-4
description: "Fourth level caller in deep call chain test"
context: fork
model: sonnet
allowed-tools:
  - Task
---

# Deep Caller 4

This skill calls deep-caller-5.

## Workflow

1. Call deep-caller-5
2. Process results

## Subagent Calls

- deep-caller-5 (Task)
