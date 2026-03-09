# Claude Code Component Creator (CCC)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://github.com/mzdbxqh/claude-code-component-creator)

A powerful Claude Code plugin for creating high-quality components and skills with a structured Intent/Blueprint/Delivery workflow.

[中文文档](README_zh.md)

## Features

- **Three-Stage Workflow**: Intent → Blueprint → Delivery ensures design quality
- **76+ Antipattern Checks**: Comprehensive quality review across 8 dimensions
- **Meta-Reflection Framework**: 4-dimensional self-assessment for quality assurance
- **Dual-Model Validation**: Sonnet generates, Haiku validates
- **Traceability Matrix**: Complete tracking from requirements to implementation
- **External State Management**: Workflow state stored in YAML files

## Quick Start

### Installation

1. Install [Claude Code](https://claude.ai/code)
2. Clone this repository:
```bash
git clone https://github.com/mzdbxqh/claude-code-component-creator.git
```
3. Load the plugin in Claude Code

### Create Your First Component

```bash
# Complete workflow in one command
/ccc:quick

# Or step by step
/ccc:init          # Create intent
/ccc:design        # Generate blueprint
/ccc:build         # Create deliverable
/ccc:review        # Quality check
```

## Core Workflow

```
Intent (What to build)
  ↓
Blueprint (How to build)
  ↓
Delivery (Implementation)
  ↓
Review (Quality assurance)
```

## Commands

| Command | Description |
|---------|-------------|
| `/ccc:init` | Create intent artifact using 4-question framework |
| `/ccc:design` | Generate blueprint from intent |
| `/ccc:build` | Create production-ready deliverable |
| `/ccc:review` | Comprehensive quality review (76+ checks) |
| `/ccc:quick` | Execute complete workflow in one command |
| `/ccc:iterate` | Iterate on existing blueprint |
| `/ccc:status` | Display project workflow state |
| `/ccc:trace` | Generate traceability matrix |
| `/ccc:validate` | Validate artifacts with external tools |

See [full command reference](commands/) for details.

## Quality Dimensions

| Dimension | Weight | Rules | Description |
|-----------|--------|-------|-------------|
| Intent Matching | 10% | 4 | Trigger scenarios, synonyms, exclusions |
| Configuration | 15% | 5 | Setup requirements, examples, error handling |
| Dependencies | 15% | 12 | Runtime deps, external APIs, toolchain |
| Security | 20% | 5 | Command injection, sensitive data, permissions |
| Environment | 15% | 3 | OS/shell compatibility, path separators |
| LLM Compatibility | 15% | 3 | Model-specific features, blocking checks |
| Scalability | 10% | 4 | Token usage, batching, timeouts |
| Architecture | Extra | 15 | Workflow/component/responsibility design |

## Documentation

- [Migration Guide](docs/v3-migration-guide.md) - Upgrade from v2.0 to v3.0
- [Best Practices](docs/best-practices/ccc-best-practices.md) - Usage guidelines
- [User Guides](docs/user-guide/) - Detailed command documentation
- [Templates](docs/templates/) - Intent/Blueprint/Delivery templates

## Examples

See [test-fixtures/](test-fixtures/) for example components.

## Development

```bash
# Run tests
/ccc:test-sandbox

# Review plugin quality
/ccc:review
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.

Copyright (c) 2026 showme.cc

## Maintainer

- **mzdbxqh** - [GitHub](https://github.com/mzdbxqh)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
