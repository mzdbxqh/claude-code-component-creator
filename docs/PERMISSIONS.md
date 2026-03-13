# CCC Permissions Documentation

**Version**: 3.0.0
**Last Updated**: 2026-03-11

## Overview

CCC (Claude Code Component Creator) follows the **principle of least privilege** for all components. This document describes the permission model and guidelines for declaring tool permissions.

## Permission Fields

### Skills: `allowed-tools`

Skills use the `allowed-tools` field to declare required tools:

```yaml
---
name: ccc:cmd-review
description: "Execute comprehensive quality review"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Task
---
```

### SubAgents: `tools`

SubAgents use the `tools` field to declare required tools:

```yaml
---
name: review-core
description: "Core review logic"
model: haiku
tools:
  - Read
  - Grep
  - Glob
  - Write
permissionMode: prompt
---
```

### Permission Mode

SubAgents must specify `permissionMode`:
- **prompt**: Ask user for permission before each tool use (recommended for sensitive operations)
- **auto**: Automatically grant permissions (use only for trusted, non-sensitive operations)

## Tool Categories

### Read-Only Tools
Safe for most operations:
- `Read`: Read files
- `Grep`: Search file contents
- `Glob`: Find files by pattern

### Write Tools
Require careful permission management:
- `Write`: Create/overwrite files
- `Edit`: Modify existing files

### Execution Tools
High-risk, require `permissionMode: prompt`:
- `Bash`: Execute shell commands
- `Task`: Launch SubAgents

### Network Tools
Require explicit user consent:
- `WebFetch`: Fetch web content
- `WebSearch`: Search the web

### Other Tools
- `AskUserQuestion`: Interactive prompts (safe)
- `NotebookEdit`: Edit Jupyter notebooks (write operation)

## Permission Design Principles

### 1. Least Privilege

Only declare tools that are **actually used** in the component:

❌ **Bad**: Declaring unused tools
```yaml
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  # Component only uses Read and Grep
```

✅ **Good**: Only necessary tools
```yaml
allowed-tools:
  - Read
  - Grep
```

### 2. Explicit Over Implicit

Never use wildcard permissions:

❌ **Bad**: Wildcard
```yaml
allowed-tools:
  - "*"  # Grants all tools
```

✅ **Good**: Explicit list
```yaml
allowed-tools:
  - Read
  - Write
```

### 3. Permission Mode Selection

Choose appropriate `permissionMode` for SubAgents:

**Use `prompt`** for:
- Components using `Bash`, `Write`, `Edit`
- Components modifying user files
- Components with external API calls
- Any sensitive operations

**Use `auto`** for:
- Read-only operations (`Read`, `Grep`, `Glob`)
- Trusted internal operations
- No file modifications or command execution

### 4. Granular Permissions

Prefer multiple focused components over one component with excessive permissions:

❌ **Bad**: One component, many permissions
```yaml
name: do-everything
allowed-tools:
  - Read
  - Write
  - Bash
  - WebFetch
```

✅ **Good**: Separate components
```yaml
# Component 1: Analysis
name: analyzer
allowed-tools:
  - Read
  - Grep

# Component 2: Implementation
name: implementer
allowed-tools:
  - Write
  - Edit
```

## CCC Component Permissions

### Command Skills (cmd-*)

Commands orchestrate workflows and typically need:
- `Task`: Launch SubAgents
- `Read`, `Glob`, `Grep`: File analysis
- `Write`: Create artifacts

Example: `cmd-review`
```yaml
allowed-tools:
  - Read
  - Glob
  - Grep
  - Task
```

### Standard Skills (std-*)

Standards provide reference data, typically read-only:
- `Read`: Access knowledge base

Example: `std-naming-rules`
```yaml
allowed-tools:
  - Read
```

### Library Skills (lib-*)

Libraries provide data collections, typically read-only:
- `Read`: Access pattern/antipattern files
- `Glob`: Find relevant rules

Example: `lib-antipatterns`
```yaml
allowed-tools:
  - Read
  - Glob
```

### SubAgents

SubAgents execute tasks and vary by function:

**Review/Analysis** (read-only):
```yaml
tools:
  - Read
  - Grep
  - Glob
permissionMode: auto
```

**Report Generation** (write operations):
```yaml
tools:
  - Read
  - Write
permissionMode: prompt
```

**Code Modification** (high-risk):
```yaml
tools:
  - Read
  - Edit
  - Bash
permissionMode: prompt
```

## Permission Verification

### Check Component Permissions

Use the review command to verify permissions:
```bash
/cmd-review skills/my-skill/
```

The review will check:
- PERM-001: Excessive permissions (declared but unused)
- PERM-002: Permission inconsistency (used but not declared)
- PERM-003: Permission syntax errors
- PERM-004: Sensitive tool protection (missing `permissionMode`)

### Audit All Permissions

List all component permissions:
```bash
# Skills
grep -h "^allowed-tools:" skills/*/SKILL.md

# SubAgents
grep -h "^tools:" agents/*/SKILL.md agents/*/*/SKILL.md
```

## Security Best Practices

### 1. Never Skip Permission Checks

Don't bypass permission prompts in production:
```yaml
# ❌ Dangerous for sensitive operations
permissionMode: auto
tools:
  - Bash
  - Write

# ✅ Safe: User confirms each action
permissionMode: prompt
tools:
  - Bash
  - Write
```

### 2. Validate External Input

When using tools with external input, validate first:
```python
# ❌ Bad: Direct command execution
bash_tool(user_input)

# ✅ Good: Validate and sanitize
if is_safe_path(user_input):
    bash_tool(f"ls {shell_escape(user_input)}")
```

### 3. Document Why Permissions Are Needed

In SKILL.md, explain why each tool is required:
```yaml
# Example: cmd-review
allowed-tools:
  - Read    # Read component files
  - Grep    # Search for patterns
  - Glob    # Find component files
  - Task    # Launch review-core SubAgent
```

### 4. Regular Permission Audits

Periodically review and minimize permissions:
```bash
# Run CCC review on itself
/cmd-review .

# Check for PERM-001 violations (unused tools)
```

## Common Permission Patterns

### Pattern 1: Read-Only Analysis
```yaml
allowed-tools:
  - Read
  - Grep
  - Glob
```
**Use for**: Code analysis, documentation, reporting

### Pattern 2: Report Generation
```yaml
tools:
  - Read
  - Write
permissionMode: prompt
```
**Use for**: Creating reports, documentation

### Pattern 3: Code Modification
```yaml
tools:
  - Read
  - Edit
  - Bash  # For testing changes
permissionMode: prompt
```
**Use for**: Refactoring, fixing code

### Pattern 4: Workflow Orchestration
```yaml
allowed-tools:
  - Read
  - Task
```
**Use for**: Commands that delegate to SubAgents

## Troubleshooting

### Permission Denied Errors

**Problem**: Tool use rejected
```
Error: Permission denied for tool 'Write'
```

**Solution**: Add tool to `allowed-tools` or `tools` list:
```yaml
allowed-tools:
  - Read
  - Write  # Add this
```

### Too Many Permissions

**Problem**: CCC review shows PERM-001 warnings
```
PERM-001: Tool 'Bash' declared but never used
```

**Solution**: Remove unused tools:
```yaml
# Before
allowed-tools:
  - Read
  - Bash  # Remove if not used

# After
allowed-tools:
  - Read
```

### Missing Permission Mode

**Problem**: CCC review shows PERM-004 error
```
PERM-004: SubAgent uses sensitive tools without permissionMode
```

**Solution**: Add `permissionMode` to SubAgent frontmatter:
```yaml
---
name: my-agent
tools:
  - Bash
permissionMode: prompt  # Add this
---
```

## References

- [Official Security Standards](markdown_docs/permissions.md)
- [PERM-001: Excessive Permissions](agents/reviewer/knowledge/antipatterns/security/PERM-001.yaml)
- [PERM-002: Permission Inconsistency](agents/reviewer/knowledge/antipatterns/security/PERM-002.yaml)
- [PERM-003: Permission Syntax](agents/reviewer/knowledge/antipatterns/security/PERM-003.yaml)
- [PERM-004: Sensitive Tool Protection](agents/reviewer/knowledge/antipatterns/security/PERM-004.yaml)

## Contributing

When adding new components to CCC:

1. **Identify Required Tools**: List all tools the component needs
2. **Follow Least Privilege**: Only include necessary tools
3. **Set Permission Mode**: Choose appropriate mode for SubAgents
4. **Document Reasoning**: Explain why each tool is needed
5. **Test Permissions**: Verify component works with declared permissions
6. **Review**: Run `/cmd-review` to check for permission issues

---

**Maintainer**: mzdbxqh
**License**: MIT
**Last Review**: 2026-03-11
