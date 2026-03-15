# Claude Code Component Creator (CCC)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-3.2.0-blue.svg)](https://github.com/mzdbxqh/claude-code-component-creator)
[![Quality Score](https://img.shields.io/badge/quality-96%2F100-brightgreen.svg)](docs/reviews/)

A powerful Claude Code plugin for creating high-quality components and skills with a structured Intent/Blueprint/Delivery workflow.

[中文文档](README_zh.md)

## Features

- **Three-Stage Workflow**: Intent → Blueprint → Delivery ensures design quality
- **77+ Antipattern Checks**: Comprehensive quality review across 8 dimensions
- **Meta-Reflection Framework**: 4-dimensional self-assessment for quality assurance
- **Dual-Model Validation**: Sonnet generates, Haiku validates
- **Traceability Matrix**: Complete tracking from requirements to implementation
- **External State Management**: Workflow state stored in YAML files
- **Parallel Processing**: 3.75x-6.8x speedup for large projects
- **Token Budget Transparency**: Complete cost estimation and optimization guides
- **Checkpoint Recovery**: Resume long-running workflows from interruptions
- **Performance Benchmarking**: Built-in performance testing framework
- **Plugin Profiler Framework**: Automatic plugin profiling with standardized metadata extraction

## Quick Start

### Installation

1. Install [Claude Code](https://claude.ai/code)
2. Clone this repository:
```bash
git clone https://github.com/mzdbxqh/claude-code-component-creator.git
```
3. Load the plugin in Claude Code

### Installation Details

#### Prerequisites
- **Claude Code**: Version 0.1.0 or higher
- **Operating System**: macOS, Linux, or Windows (via WSL)
- **Git**: For cloning and version control
- **Node.js**: (Optional) For some advanced features

#### Plugin Directory Structure
```
claude-code-component-creator/
├── agents/          # SubAgent definitions
├── skills/          # Skill definitions
├── hooks/           # Hook configurations
├── docs/            # Documentation
└── test-fixtures/   # Example components
```

#### Verification
After installation, verify the plugin is loaded:
```bash
# List all available commands
/help

# You should see /cmd-* commands in the list
```

#### Common Installation Issues
- **Plugin not found**: Ensure the plugin directory is in Claude Code's plugin path
- **Permission errors**: Check directory permissions (755 for directories, 644 for files)
- **Path issues**: Use absolute paths or ensure relative paths are correct

See [Troubleshooting](#troubleshooting) for more help.

### Create Your First Component

```bash
# Complete workflow in one command
/cmd-quick

# Or step by step
/cmd-init          # Create intent
/cmd-design        # Generate blueprint
/cmd-build         # Create deliverable
/cmd-review        # Quality check
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



See [full command reference](skills/) for details.

## Configuration

CCC can be configured through various methods:

### Plugin Configuration

Create `.claude-plugin/config.json` to customize plugin behavior:
```json
{
  "name": "claude-code-component-creator",
  "version": "3.2.0",
  "settings": {
    "default_model": "sonnet",
    "artifacts_dir": ".ccc/artifacts",
    "review_threshold": 80
  }
}
```

### Environment Variables

CCC respects the following environment variables:
- `CCC_ARTIFACTS_DIR`: Override default artifacts directory (default: `.ccc/artifacts`)
- `CCC_REVIEW_THRESHOLD`: Minimum review score for passing (default: 80)
- `CCC_DEFAULT_MODEL`: Default model for SubAgents (default: `sonnet`)
- `SLASH_COMMAND_TOOL_CHAR_BUDGET`: Maximum characters for skill descriptions (default: 16000)

### Workflow State

Workflow state is stored in YAML files:
```
.ccc/artifacts/
├── intent-*.yaml       # Intent artifacts
├── blueprint-*.yaml    # Blueprint artifacts
└── delivery-*.yaml     # Delivery artifacts
```

### Hooks Configuration

Configure hooks in `hooks/config.json`:
```json
{
  "hooks": [
    {
      "event": "PreToolUse",
      "matcher": {"tool": "Bash"},
      "type": "command",
      "command": "security-check.sh"
    }
  ]
}
```

See [Hooks Documentation](docs/hooks.md) for more details.

## Plugin Profiler Framework

CCC introduces an automated plugin profiling system that enhances review reports with comprehensive plugin metadata.

### Overview

When you run `/cmd-review` on a plugin, CCC now automatically:
1. Extracts plugin metadata (name, version, positioning, architecture)
2. Analyzes component structure (skills, agents, hooks)
3. Identifies workflow mechanisms and activation patterns
4. Evaluates documentation completeness (0-100 score)
5. Generates standardized plugin profile (JSON + Markdown)
6. Embeds "Plugin Overview" chapter in review reports

### Plugin Profile Output

```
docs/profile/
├── plugin-profile.json       # Structured metadata (JSON Schema validated)
└── plugin-profile.md          # Human-readable report
```

### Profile Contents

The plugin profile includes:

- **Meta Information**: Name, version, positioning, base framework
- **Architecture Design**: Component statistics, classification system, workflow mechanism
- **Usage Methods**: Slash commands, auto-activation skills
- **Core Philosophy**: Design principles and rationale
- **System Requirements**: Platform, dependencies, compatibility
- **Quality Metrics**: Documentation completeness score and recommendations

### New Review Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--skip-profiling` | boolean | false | Skip plugin profiling (advanced users) |
| `--profile-only` | boolean | false | Only generate profile, skip quality review |
| `--profile-output` | path | docs/profile/ | Profile output directory |

### Example Usage

```bash
# Standard review (with profiling)
/cmd-review

# Profile-only mode (no quality review)
/cmd-review --profile-only

# Review without profiling
/cmd-review --skip-profiling

# Custom output directory
/cmd-review --profile-output=custom/path/
```

### Self-Explanation Validation

Review reports now include automatic self-explanation validation:

- **Completeness Check** (40%): All required sections present
- **Self-Containment Check** (30%): No external references
- **Structure Clarity** (20%): Clear heading hierarchy
- **Information Accuracy** (10%): Consistent data across sections

Reports are scored 0-100, with recommendations for improvement.

### Benefits

- **Improved Report Clarity**: Reports are now self-explanatory and can be read independently
- **Better Plugin Understanding**: Comprehensive overview before diving into details
- **Quality Transparency**: Documentation completeness scored objectively
- **Standardized Metadata**: Consistent plugin profiling across all plugins

See [Plugin Profiler Documentation](agents/profiler/plugin-profiler/SKILL.md) for implementation details.

## Quality Dimensions

CCC achieves **96/100** overall quality score with comprehensive 8-dimension checks:

| Dimension | Weight | Rules | Score | Description |
|-----------|--------|-------|-------|-------------|
| Intent Matching | 10% | 4 | 95/100 | Trigger scenarios, synonyms, exclusions |
| Configuration | 15% | 5 | 97/100 | Setup requirements, examples, error handling |
| Dependencies | 15% | 12 | 94/100 | Runtime deps, external APIs, toolchain |
| Security | 20% | 7 | 98/100 | Command injection prevention, audit logging |
| Environment | 15% | 3 | 93/100 | OS/shell compatibility, path separators |
| LLM Compatibility | 15% | 3 | 96/100 | Token budget, model optimization |
| Scalability | 10% | 4 | 96/100 | Parallel processing, batching, timeouts |
| Testability | Extra | 20 | 95/100 | Test coverage, evals.json framework |

## Documentation

- [Migration Guide](docs/v3-migration-guide.md) - Upgrade from v2.0 to v3.0
- [Best Practices](docs/best-practices/ccc-best-practices.md) - Usage guidelines
- [User Guides](docs/user-guide/) - Detailed command documentation
- [Templates](docs/templates/) - Intent/Blueprint/Delivery templates
- [Release Workflow](docs/github-release-workflow.md) - Standard release process

## Examples

See [test-fixtures/](test-fixtures/) for example components.

## Development

```bash
# Run tests
/cmd-test-sandbox

# Review plugin quality
/cmd-review
```

## Troubleshooting

### Common Issues

#### Plugin Not Loading

**Symptoms**: `/cmd-*` commands not available

**Solutions**:
1. Verify plugin directory is in Claude Code's plugin path
2. Check directory structure is correct
3. Restart Claude Code
4. Check for syntax errors in SKILL.md files:
   ```bash
   yamllint skills/*/SKILL.md agents/*/SKILL.md
   ```

#### Command Execution Fails

**Symptoms**: Command starts but fails with error

**Solutions**:
1. Check command permissions in SKILL.md frontmatter
2. Verify all required tools are in `allowed-tools` or `tools` list
3. Check logs for detailed error messages
4. Try with `--verbose` flag if available

#### Review Fails with Low Score

**Symptoms**: `/cmd-review` shows many errors

**Solutions**:
1. Read the review report carefully - it shows specific issues
2. Focus on ERROR level issues first
3. Check official documentation for violated standards
4. Use `/cmd-fix` to auto-fix some issues:
   ```bash
   /cmd-fix --report review-report.md
   ```

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for complete troubleshooting guide.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.

Copyright (c) 2026 showme.cc

## Maintainer

- **mzdbxqh** - [GitHub](https://github.com/mzdbxqh/claude-code-component-creator)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

**Version**: 3.2.0 | **Quality Score**: 96/100 | **License**: MIT
