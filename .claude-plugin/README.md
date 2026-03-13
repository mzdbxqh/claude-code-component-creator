# CCC Plugin v3.0

Claude Code Component Creator v3.0 - Intent/Blueprint/Delivery workflow with meta-reflection.

## Overview

CCC v3.0 introduces a three-stage workflow for creating high-quality Claude Code components:

1. **Intent** - Clarify requirements using 4-question framework
2. **Blueprint** - Technical design with dual-model verification
3. **Delivery** - Actual implementation with built-in review

## Quick Start

```bash
/cmd-quick "我要做一个自动部署工具，支持Kubernetes"
```

## Commands

### Core Workflow
- `/cmd-init` - Create Intent artifact (4-question framework)
- `/cmd-design` - Generate Blueprint from Intent
- `/cmd-build` - Generate Delivery from Blueprint

### Status & Monitoring
- `/cmd-status` - View project artifact status
- `/cmd-status-graph` - Visual dependency graph
- `/cmd-status-trace` - Traceability matrix

### Iteration & Comparison
- `/cmd-iterate` - Iterate on existing Blueprint
- `/cmd-diff` - Compare artifact versions

### Quality Assurance
- `/cmd-validate` - Validate current artifact
- `/cmd-review` - Deep review with dual-model validation
- `/cmd-trace` - Generate traceability matrix

### Quick Start
- `/cmd-quick` - Full workflow in one command

## Architecture

```
┌─────────┐    ┌──────────┐    ┌─────────┐
│  Intent │───▶│ Blueprint│───▶│ Delivery│
└─────────┘    └──────────┘    └─────────┘
     │               │               │
     ▼               ▼               ▼
  4-questions    Checkpoint      Review
                 (dual-model)    (57 antipatterns)
```

## Key Features

- **Meta-reflection framework** - Self-assessment against 4 dimensions
- **External state management** - Workflow state stored in YAML
- **Dual-model verification** - Sonnet generates, Haiku validates
- **76+ antipatterns** - Comprehensive quality checks across 8 dimensions
- **Cognitive load management** - must_remember fields

## Directory Structure

```
.claude-plugin/
├── plugin.json          # Plugin metadata
└── README.md            # This file

commands/                # User-facing commands
├── ccc-init.md
├── ccc-design.md
├── ccc-build.md
└── ...

agents/                  # Subagents
├── intent-core/         # Stage 1: Intent creation
├── blueprint-core/      # Stage 2: Blueprint generation
├── delivery-core/       # Stage 3: Delivery generation
├── checkpoint-core/     # Built-in validation
├── review-core/         # Deep review
└── workflow-engine/     # State management

docs/ccc/                # Artifact storage
├── intent/              # Intent artifacts
├── blueprint/           # Blueprint artifacts
├── delivery/            # Delivery artifacts
└── workflow-state/      # Workflow state files

templates/               # Templates
├── intent-v3.0.yaml
├── blueprint-v3.0.yaml
├── delivery-v3.0.yaml
├── reflection-policy-v3.0.yaml
└── workflow-state-schema.yaml
```

## Migration from v2.0

See [v3-migration-guide.md](../docs/v3-migration-guide.md) for details.

| v2.0 Command    | v3.0 Equivalent |
|-----------------|-----------------|
| /design-new     | /cmd-init → /cmd-design |
| /design-iterate | /cmd-iterate    |
| /review         | /cmd-review     |

## License

MIT
