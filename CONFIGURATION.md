# CCC Configuration Guide

**Version**: 3.0.0
**Last Updated**: 2026-03-11

Complete guide to configuring Claude Code Component Creator (CCC).

---

## Table of Contents

1. [Plugin Configuration](#plugin-configuration)
2. [Environment Variables](#environment-variables)
3. [Workflow State Management](#workflow-state-management)
4. [Hooks Configuration](#hooks-configuration)
5. [Skills Configuration](#skills-configuration)
6. [SubAgents Configuration](#subagents-configuration)
7. [Advanced Configuration](#advanced-configuration)

---

## Plugin Configuration

### .claude-plugin/config.json

Main plugin configuration file:

```json
{
  "name": "claude-code-component-creator",
  "version": "3.0.0",
  "description": "Meta-plugin for creating high-quality Claude Code components",
  "author": "mzdbxqh",
  "license": "MIT",
  "settings": {
    "default_model": "sonnet",
    "artifacts_dir": ".ccc/artifacts",
    "review_threshold": 80,
    "max_parallel_agents": 3,
    "enable_hooks": true
  },
  "dependencies": {
    "claude_code": ">=0.1.0"
  }
}
```

### Configuration Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `default_model` | string | `"sonnet"` | Default model for SubAgents (sonnet/opus/haiku) |
| `artifacts_dir` | string | `".ccc/artifacts"` | Directory for workflow artifacts |
| `review_threshold` | number | `80` | Minimum review score for passing (0-100) |
| `max_parallel_agents` | number | `3` | Maximum concurrent SubAgents |
| `enable_hooks` | boolean | `true` | Enable/disable hooks system |

---

## Environment Variables

CCC respects the following environment variables:

### Core Variables

```bash
# Artifacts directory override
export CCC_ARTIFACTS_DIR="/custom/path/to/artifacts"

# Review threshold (0-100)
export CCC_REVIEW_THRESHOLD=85

# Default model for SubAgents
export CCC_DEFAULT_MODEL=sonnet  # sonnet|opus|haiku

# Enable/disable debug logging
export CCC_DEBUG=1  # 0 or 1

# Log level
export CCC_LOG_LEVEL=info  # debug|info|warn|error

# Cache directory
export CCC_CACHE_DIR="$HOME/.ccc/cache"
```

### Skill-Specific Variables

```bash
# Maximum characters for skill descriptions
export SLASH_COMMAND_TOOL_CHAR_BUDGET=16000

# Token budget percentage of context window
export CCC_SKILL_BUDGET_PERCENT=2  # 2% of context window
```

### Workflow Variables

```bash
# Workflow state format
export CCC_STATE_FORMAT=yaml  # yaml|json

# Enable workflow validation
export CCC_VALIDATE_TRANSITIONS=1

# Workflow timeout (seconds)
export CCC_WORKFLOW_TIMEOUT=300
```

### Hook Variables

```bash
# Hooks configuration file
export CCC_HOOKS_CONFIG="hooks/hooks.json"

# Enable/disable specific hook types
export CCC_ENABLE_PRE_TOOL_HOOKS=1
export CCC_ENABLE_POST_TOOL_HOOKS=1

# Hook timeout (milliseconds)
export CCC_HOOK_TIMEOUT=5000
```

### Setting Environment Variables

**Temporary (current session)**:
```bash
export CCC_REVIEW_THRESHOLD=90
```

**Permanent (add to shell profile)**:
```bash
# ~/.bashrc or ~/.zshrc
export CCC_ARTIFACTS_DIR="$HOME/.ccc/artifacts"
export CCC_DEFAULT_MODEL=sonnet
```

**Project-specific (.env file)**:
```bash
# .env in project root
CCC_REVIEW_THRESHOLD=85
CCC_DEBUG=1
```

---

## Workflow State Management

### Artifacts Directory Structure

```
.ccc/artifacts/
├── intent-001.yaml          # Intent artifacts
├── intent-002.yaml
├── blueprint-001.yaml       # Blueprint artifacts
├── blueprint-002.yaml
├── delivery-001.yaml        # Delivery artifacts
└── .metadata/              # Internal metadata
    ├── workflow-state.json
    └── artifact-index.json
```

### Artifact Naming Convention

- **Intent**: `intent-{id}.yaml`
- **Blueprint**: `blueprint-{id}.yaml`
- **Delivery**: `delivery-{id}.yaml`

ID format: Zero-padded 3-digit number (001, 002, ...)

### Workflow State File

`.ccc/artifacts/.metadata/workflow-state.json`:

```json
{
  "current_phase": "blueprint",
  "active_artifacts": {
    "intent": "intent-001",
    "blueprint": "blueprint-001"
  },
  "history": [
    {
      "timestamp": "2026-03-11T10:00:00Z",
      "action": "create_intent",
      "artifact": "intent-001"
    },
    {
      "timestamp": "2026-03-11T10:30:00Z",
      "action": "create_blueprint",
      "artifact": "blueprint-001",
      "parent": "intent-001"
    }
  ]
}
```

### Configuration

```bash
# Configure artifacts directory
export CCC_ARTIFACTS_DIR="/custom/path"

# Configure state format
export CCC_STATE_FORMAT=yaml  # or json

# Enable/disable state tracking
export CCC_ENABLE_STATE_TRACKING=1
```

---

## Hooks Configuration

### hooks/hooks.json

Main hooks configuration:

```json
{
  "hooks": [
    {
      "event": "PreToolUse",
      "matcher": {
        "tool": "Bash"
      },
      "type": "command",
      "command": "hooks/scripts/security-check.sh",
      "timeout": 5000,
      "description": "Security validation for Bash commands"
    },
    {
      "event": "PostToolUse",
      "matcher": {
        "tool": "(Write|Edit)"
      },
      "type": "command",
      "command": "hooks/scripts/backup.sh",
      "timeout": 3000,
      "description": "Backup files after modifications"
    },
    {
      "event": "PreToolUse",
      "matcher": {
        "tool": ".*"
      },
      "type": "prompt",
      "prompt": "Is this tool use safe? Check for security implications.",
      "timeout": 10000
    }
  ]
}
```

### Hook Types

| Type | Description | Use Case |
|------|-------------|----------|
| `command` | Execute shell script | Security checks, backups, validation |
| `prompt` | LLM-based evaluation | Complex policy decisions |
| `agent` | Full SubAgent | Advanced validation logic |

### Supported Events

| Event | When Triggered | Common Use Cases |
|-------|----------------|------------------|
| `PreToolUse` | Before tool execution | Security validation, permission checks |
| `PostToolUse` | After tool execution | Logging, backups, result validation |
| `UserPromptSubmit` | Before processing user input | Input sanitization, policy enforcement |
| `SubagentStart` | SubAgent initialization | Resource allocation, setup |
| `SubagentStop` | SubAgent termination | Cleanup, logging |
| `PermissionRequest` | Permission dialog | Custom authorization logic |

### Matcher Configuration

```json
{
  "matcher": {
    "tool": "Bash",              // Exact match
    "tool": "(Bash|Write)",      // Multiple tools (regex)
    "tool": ".*",                // All tools
    "arg_pattern": "rm.*"        // Argument pattern
  }
}
```

### Exit Codes

Hooks use standard exit codes:
- **0**: Success, continue execution
- **1**: Failure, abort execution
- **2**: Warning, continue with logging

See [hooks/README.md](hooks/README.md) for details.

---

## Skills Configuration

### Skill Frontmatter

```yaml
---
name: ccc:my-skill
description: "Brief description with trigger keywords (100-150 chars recommended)"
allowed-tools:
  - Read
  - Grep
  - Glob
disable-model-invocation: true  # For command-like skills
---
```

### Field Reference

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | Yes | string | Skill name (must start with prefix) |
| `description` | Yes | string | Brief description (100-150 chars) |
| `allowed-tools` | Yes | array | List of allowed tools |
| `disable-model-invocation` | No | boolean | Disable model for command-like skills |

### Naming Convention

- **Commands**: `ccc:cmd-{name}` - User-invocable commands
- **Standards**: `ccc:std-{name}` - Reference standards/rules
- **Libraries**: `ccc:lib-{name}` - Data collections

### Description Guidelines

✅ **Good** (concise, clear triggers):
```yaml
description: "Review component quality across 8 dimensions. Use when: design complete, before deployment."
```

❌ **Bad** (too long, unclear):
```yaml
description: "This skill performs a comprehensive quality review of components including checking for antipatterns, validating configurations, analyzing dependencies, assessing security posture, checking environment compatibility, verifying LLM integration, evaluating scalability, and testing capabilities across multiple dimensions with detailed reporting..."
```

### Token Budget

Skills are subject to token budget limits:
- **Default**: 16,000 characters
- **Calculated**: 2% of context window
- **Environment variable**: `SLASH_COMMAND_TOOL_CHAR_BUDGET`

```bash
# Increase budget if needed
export SLASH_COMMAND_TOOL_CHAR_BUDGET=20000
```

---

## SubAgents Configuration

### SubAgent Frontmatter

```yaml
---
name: my-subagent
description: "What this SubAgent does. Trigger: keywords/scenario."
model: sonnet  # sonnet|opus|haiku|inherit
tools:
  - Read
  - Write
  - Bash
permissionMode: prompt  # prompt|auto
skills:
  - ccc:lib-antipatterns
  - ccc:std-naming-rules
memory: true  # Enable memory (optional)
---
```

### Field Reference

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | Yes | string | SubAgent name (kebab-case) |
| `description` | Yes | string | Purpose and trigger scenarios |
| `model` | No | string | Model selection (default: inherit) |
| `tools` | Yes | array | Required tools |
| `permissionMode` | Yes | string | Permission handling mode |
| `skills` | No | array | Pre-loaded skills |
| `memory` | No | boolean | Enable conversation memory |

### Model Selection

| Model | Use Case | Cost | Speed |
|-------|----------|------|-------|
| `inherit` | Most cases (recommended) | Varies | Varies |
| `haiku` | Simple, fast tasks | Low | Fast |
| `sonnet` | Medium complexity | Medium | Medium |
| `opus` | Complex reasoning | High | Slow |

**Recommendation**: Use `inherit` for flexibility, only specify when specific model needed.

### Permission Modes

**prompt** (Recommended for sensitive operations):
- User confirms each tool use
- Suitable for: Bash, Write, Edit, WebFetch
- Example: Code modification, file deletion

**auto** (For trusted, safe operations):
- Automatic permission grant
- Suitable for: Read, Grep, Glob
- Example: Read-only analysis

⚠️ **Never** use `auto` with `Bash`, `Write`, or `Edit` unless absolutely necessary.

---

## Advanced Configuration

### Custom Antipattern Rules

Add custom rules to `agents/reviewer/knowledge/antipatterns/custom/`:

```yaml
# custom-rule.yaml
id: CUSTOM-001
name: my-custom-rule
severity: warning
component_type: skill
category: custom

detection:
  method: regex
  pattern: "forbidden-pattern"

fix:
  automatic: false
  suggestion: "Remove forbidden pattern"
```

### Custom Hooks

Create custom hook scripts in `hooks/scripts/`:

```bash
#!/bin/bash
# custom-hook.sh

# Read environment variables
TOOL_NAME="${TOOL_NAME}"
TOOL_ARGS="${TOOL_ARGS}"

# Your validation logic here
if [[ "$TOOL_ARGS" =~ dangerous-pattern ]]; then
  echo "[ERROR] Dangerous pattern detected" >&2
  exit 1
fi

exit 0
```

Register in `hooks/hooks.json`:
```json
{
  "event": "PreToolUse",
  "script": "hooks/scripts/custom-hook.sh",
  "timeout": 5000
}
```

### Review Configuration

Configure review behavior:

```bash
# Review threshold (minimum score to pass)
export CCC_REVIEW_THRESHOLD=80

# Enable specific dimensions
export CCC_REVIEW_INTENT=1
export CCC_REVIEW_CONFIG=1
export CCC_REVIEW_SECURITY=1

# Output format
export CCC_REVIEW_FORMAT=markdown  # markdown|json

# Severity filter
export CCC_REVIEW_MIN_SEVERITY=warning  # error|warning|info
```

### Performance Tuning

```bash
# Maximum concurrent SubAgents
export CCC_MAX_PARALLEL_AGENTS=3

# Cache settings
export CCC_ENABLE_CACHE=1
export CCC_CACHE_TTL=3600  # seconds

# Timeout settings
export CCC_SUBAGENT_TIMEOUT=300  # seconds
export CCC_HOOK_TIMEOUT=5000     # milliseconds
```

---

## Configuration Files Locations

| File | Location | Purpose |
|------|----------|---------|
| Plugin config | `.claude-plugin/config.json` | Main plugin settings |
| Hooks config | `hooks/hooks.json` | Hooks configuration |
| Environment | `.env` | Environment variables |
| Workflow state | `.ccc/artifacts/.metadata/workflow-state.json` | Workflow tracking |
| Skill frontmatter | `skills/*/SKILL.md` | Skill configuration |
| SubAgent frontmatter | `agents/*/SKILL.md` | SubAgent configuration |

---

## Troubleshooting Configuration

### Common Issues

**Problem**: Configuration not loaded
```bash
# Check config file syntax
cat .claude-plugin/config.json | jq .
```

**Problem**: Environment variables not working
```bash
# Verify variables are set
env | grep CCC_
```

**Problem**: Hooks not executing
```bash
# Check hooks configuration
cat hooks/hooks.json | jq .

# Verify script permissions
ls -l hooks/scripts/
```

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more help.

---

## Best Practices

1. **Start with Defaults**: Use default configuration, customize only when needed
2. **Document Changes**: Comment why you changed settings
3. **Version Control**: Commit `.claude-plugin/config.json` and `hooks/hooks.json`
4. **Test After Changes**: Run `/cmd-review .` after configuration changes
5. **Security First**: Review security implications of configuration changes
6. **Use Environment Variables**: For machine-specific or sensitive settings

---

## References

- [Installation Guide](README.md#installation)
- [Permissions Documentation](docs/PERMISSIONS.md)
- [Security Policy](SECURITY.md)
- [Hooks Documentation](hooks/README.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

---

**Last Updated**: 2026-03-11
**Version**: 1.0.0
**Maintainer**: CCC Team
