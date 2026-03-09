---
name: deep-caller-1
description: "First level caller in deep call chain test"
context: fork
model: sonnet
allowed-tools:
  - Task
---

# Deep Caller 1

This skill calls another skill which calls another, creating a deep call chain.

## Workflow

1. Call deep-caller-2
2. Process results

## Subagent Calls

- deep-caller-2 (Task)
