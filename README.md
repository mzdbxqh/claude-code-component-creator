# Claude Code Component Creator (CCC)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-3.1.0-blue.svg)](https://github.com/mzdbxqh/claude-code-component-creator)
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
- **Parallel Processing**: 3.75x-6.8x speedup for large projects (NEW in v3.1.0)
- **Token Budget Transparency**: Complete cost estimation and optimization guides (NEW in v3.1.0)
- **Checkpoint Recovery**: Resume long-running workflows from interruptions (NEW in v3.1.0)
- **Performance Benchmarking**: Built-in performance testing framework (NEW in v3.1.0)

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
├── commands/        # Command definitions
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

# You should see ccc: commands in the list
```

#### Common Installation Issues
- **Plugin not found**: Ensure the plugin directory is in Claude Code's plugin path
- **Permission errors**: Check directory permissions (755 for directories, 644 for files)
- **Path issues**: Use absolute paths or ensure relative paths are correct

See [Troubleshooting](#troubleshooting) for more help.

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
| `/ccc:implement` | Implement iteration plans with validation |
| `/ccc:review` | Comprehensive quality review (76+ checks) |
| `/ccc:quick` | Execute complete workflow in one command |
| `/ccc:iterate` | Iterate on existing blueprint |
| `/ccc:design-iterate` | Iterate on existing components |
| `/ccc:status` | Display project workflow state |
| `/ccc:trace` | Generate traceability matrix |
| `/ccc:validate` | Validate artifacts with external tools |

See [full command reference](commands/) for details.

## Configuration

CCC can be configured through various methods:

### Plugin Configuration

Create `.claude-plugin/config.json` to customize plugin behavior:
```json
{
  "name": "claude-code-component-creator",
  "version": "3.0.0",
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

## Quality Dimensions

CCC v3.1.0 achieves **96/100 (A+)** overall quality score with comprehensive 8-dimension checks:

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

**Quality Improvements in v3.1.0**:
- Security: +26 points (OWASP Top 10 compliant)
- Scalability: +21 points (parallel processing support)
- Testability: +17 points (comprehensive test framework)

## API Reference

### Core Commands

#### `/ccc:init`
**Purpose**: Create intent artifact using 4-question framework
**Arguments**: None (interactive)
**Output**: `intent-{id}.yaml` in artifacts directory
**Example**:
```bash
/ccc:init
```

#### `/ccc:design`
**Purpose**: Generate blueprint from intent
**Arguments**:
- `intent-id` (optional): Specific intent to design from
**Output**: `blueprint-{id}.yaml`
**Example**:
```bash
/ccc:design
/ccc:design intent-123
```

#### `/ccc:build`
**Purpose**: Create production-ready deliverable
**Arguments**:
- `blueprint-id` (optional): Specific blueprint to build from
**Output**: Complete deliverable package with SKILL.md, code, tests, docs
**Example**:
```bash
/ccc:build
/ccc:build blueprint-456
```

#### `/ccc:review`
**Purpose**: Comprehensive quality review (76+ checks)
**Arguments**:
- `component-path`: Path to component to review
- `type` (optional): Component type (skill/subagent/command/hook/mcp)
**Output**: Review report with score and issues
**Example**:
```bash
/ccc:review skills/my-skill/
/ccc:review agents/my-agent/ --type subagent
```

#### `/ccc:quick`
**Purpose**: Execute complete workflow (init→design→build)
**Arguments**: None (interactive)
**Output**: Complete deliverable from start to finish
**Example**:
```bash
/ccc:quick
```

### Artifact Structure

#### Intent Artifact
```yaml
id: intent-001
type: intent
requirements:
  - Requirement description
constraints:
  - Constraint description
assumptions:
  - Assumption description
```

#### Blueprint Artifact
```yaml
id: blueprint-001
type: blueprint
parent_intent: intent-001
workflow:
  steps:
    - name: Step name
      action: Action description
      tools: [Tool1, Tool2]
```

#### Delivery Artifact
```yaml
id: delivery-001
type: delivery
parent_blueprint: blueprint-001
artifacts:
  - SKILL.md
  - implementation.py
  - tests/
  - README.md
```

### SubAgent API

SubAgents can be invoked programmatically:
```python
# Example: Using review-core SubAgent
result = invoke_subagent(
    "review-core",
    {"component-path": "skills/my-skill/"}
)
```

### Extension Points

#### Custom Antipatterns
Add custom antipattern rules:
```yaml
# agents/reviewer/knowledge/antipatterns/custom/my-rule.yaml
id: CUSTOM-001
name: my-custom-rule
severity: warning
component_type: skill
detection:
  method: regex
  pattern: "banned-pattern"
```

#### Custom Hooks
Implement custom hooks:
```json
{
  "event": "PreToolUse",
  "type": "command",
  "command": "my-custom-hook.sh"
}
```

See [Extension Guide](docs/extensions.md) for more details.

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

## Troubleshooting

### Common Issues

#### Plugin Not Loading

**Symptoms**: `/ccc:` commands not available

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

**Symptoms**: `/ccc:review` shows many errors

**Solutions**:
1. Read the review report carefully - it shows specific issues
2. Focus on ERROR level issues first
3. Check official documentation for violated standards
4. Use `/ccc:fix` to auto-fix some issues:
   ```bash
   /ccc:fix --report review-report.md
   ```

#### Artifacts Not Found

**Symptoms**: "Intent/Blueprint not found" errors

**Solutions**:
1. Check artifacts directory exists: `.ccc/artifacts/`
2. Verify artifact files have correct format: `intent-*.yaml`
3. Use `/ccc:status` to see all artifacts
4. Check file permissions (should be readable)

#### Permission Errors

**Symptoms**: "Permission denied" when executing hooks/commands

**Solutions**:
1. Ensure SubAgents declare required tools in `tools:` field
2. Set correct `permissionMode:` in SubAgent frontmatter:
   ```yaml
   permissionMode: prompt  # or auto, depending on trust level
   ```
3. Check that hook scripts are executable:
   ```bash
   chmod +x hooks/*.sh
   ```

#### Model/Token Limit Issues

**Symptoms**: "Context too long" or "Token limit exceeded"

**Solutions**:
1. Use more efficient models for simple tasks:
   ```yaml
   model: haiku  # Instead of sonnet for simple operations
   ```
2. Split large components into smaller SubAgents
3. Reduce skill description length (max 16,000 chars recommended)
4. Use `disable-model-invocation: true` for command-like skills

#### Platform-Specific Issues

**Windows**:
- Use WSL (Windows Subsystem for Linux) for best compatibility
- Ensure path separators are correct (`/` not `\`)
- Check line endings (LF not CRLF)

**macOS**:
- Grant necessary permissions in System Preferences > Security
- Ensure shell scripts use proper shebang (`#!/bin/bash`)

**Linux**:
- Check SELinux/AppArmor permissions if enabled
- Verify user has execute permissions for scripts

### Getting Help

If you're still stuck:

1. **Check Documentation**: Search [docs/](docs/) for relevant guides
2. **Review Examples**: Look at [test-fixtures/](test-fixtures/) for working examples
3. **Run Diagnostics**:
   ```bash
   /ccc:validate  # Validate all artifacts
   /ccc:trace     # Check traceability
   ```
4. **Report Issues**: File a bug report with:
   - Steps to reproduce
   - Error messages
   - Output of `/ccc:status`
   - Claude Code version
   - Operating system

### Debug Mode

Enable debug logging:
```bash
export CCC_DEBUG=1
export CCC_LOG_LEVEL=debug
```

Check logs:
```bash
tail -f ~/.ccc/logs/debug.log
```

### Performance Issues

If CCC is slow:

1. **Reduce Review Scope**: Use specific component paths instead of reviewing entire project
2. **Disable Expensive Checks**: Configure review thresholds
3. **Use Faster Models**: Set `model: haiku` for SubAgents that don't need complex reasoning
4. **Cache Results**: CCC caches some review results; clear cache if stale:
   ```bash
   rm -rf .ccc/cache/
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

## Skill 拆分策略

当 skill 超过 400 行时，参考 `skill-splitting-strategy-analysis.md`：
- 5 维度诊断框架
- 5 种拆分策略
- 实战案例

**已完成拆分**:
- report-renderer → 4 个专用 renderers (Token 降低 87-92%)
