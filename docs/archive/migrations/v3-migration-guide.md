# CCC v3.0 Migration Guide

## Overview

CCC v3.0 introduces a new Intent/Blueprint/Delivery workflow that replaces the v2.0 design-new/design-iterate commands.

## Command Mapping

| v2.0 Command | v3.0 Equivalent |
|--------------|-----------------|
| `/design-new` | `/cmd-init` → `/cmd-design` |
| `/design-iterate` | `/cmd-iterate` |
| `/review` | `/cmd-review` |
| `/review-migration` | `/cmd-review --type=migration` |

## Key Changes

### 1. Three-Stage Workflow

v3.0 splits the design process into three explicit stages:

- **Intent**: Clarify requirements using 4-question framework
- **Blueprint**: Technical design with dual-model verification
- **Delivery**: Actual implementation with built-in review

### 2. Artifact-Based

Each stage produces a persistent artifact:

- `docs/ccc/intent/{id}.yaml`
- `docs/ccc/blueprint/{id}.yaml`
- `docs/ccc/delivery/{id}/`

### 3. External State Management

Workflow state is stored externally in `docs/ccc/workflow-state/`, not in LLM context.

### 4. Meta-Reflection

All artifacts include self-assessment against 4 dimensions:

- User Experience
- Model Stability
- Accuracy
- Robustness

## Migration Steps

1. Update plugin to v3.0
2. Use `/cmd-quick` for new components
3. Existing v2.0 designs remain compatible
4. Gradually migrate to new workflow

## Backward Compatibility

v2.0 commands remain available during transition period:

- `/design-new` → redirects to `/cmd-init`
- `/design-iterate` → redirects to `/cmd-iterate`
- `/review` → redirects to `/cmd-review`
