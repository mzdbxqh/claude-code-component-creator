# Full Featured Test Plugin

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.2.3-blue.svg)](https://github.com/example/full-plugin)

A full-featured plugin for comprehensive plugin-profiler testing. This plugin is based on Superpowers 5.0.2.

## Features

- Three-stage workflow: Plan → Execute → Review
- 10+ comprehensive checks across 3 dimensions
- Meta-validation framework
- Dual-model validation (Sonnet + Haiku)

## Installation

### Prerequisites
- **Claude Code**: Version 0.1.0 or higher
- **Operating System**: macOS, Linux, or Windows (via WSL)
- **Git**: For cloning and version control

### Setup

```bash
git clone https://github.com/example/full-plugin.git
cd full-plugin
```

## Usage

### Slash Commands

- `/full:plan` - Create execution plan
- `/full:execute` - Execute plan
- `/full:review` - Review results

### Workflow

```
Plan → Execute → Review
```

The workflow is triggered automatically via SessionStart hook when state files are detected.

## Core Principles

### External State Management
Store workflow state in YAML files for recoverability and auditability.

### Complete Traceability
Every requirement is traceable to implementation through artifact chain.

### Test-Driven Development
Tests must be written before implementation code.

## Requirements

- **Platform**: Claude Code 0.1.0+
- **OS**: macOS, Linux, Windows (via WSL)
- **Dependencies**:
  - git (required)
  - node.js (optional, for advanced features)

## License

MIT License - Copyright (c) 2026
