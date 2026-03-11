# CCC Troubleshooting Guide

**Version**: 3.0.0
**Last Updated**: 2026-03-11

Comprehensive troubleshooting guide for Claude Code Component Creator (CCC).

---

## Quick Links

- [Plugin Not Loading](#plugin-not-loading)
- [Command Execution Fails](#command-execution-fails)
- [Review Issues](#review-issues)
- [Artifacts Not Found](#artifacts-not-found)
- [Permission Errors](#permission-errors)
- [Model/Token Issues](#modeltoken-issues)
- [Platform-Specific Issues](#platform-specific-issues)
- [Performance Issues](#performance-issues)
- [Hook Issues](#hook-issues)
- [Getting Help](#getting-help)

---

## Plugin Not Loading

### Symptoms
- `/ccc:` commands not available
- Claude Code doesn't recognize the plugin
- No skills appear in `/help`

### Diagnosis

```bash
# 1. Check plugin directory location
pwd

# 2. Verify directory structure
ls -la

# 3. Check for SKILL.md files
find . -name "SKILL.md" | head -5

# 4. Validate YAML syntax
for file in skills/*/SKILL.md; do
  head -20 "$file" | grep -A10 "^---$" | yamllint -
done
```

### Solutions

#### Solution 1: Verify Plugin Path
```bash
# Ensure you're in the correct directory
cd path/to/claude-code-component-creator

# Restart Claude Code
# (Restart method depends on your installation)
```

#### Solution 2: Check YAML Syntax
```bash
# Install yamllint if needed
pip install yamllint

# Check all SKILL.md files
yamllint skills/*/SKILL.md agents/*/SKILL.md
```

Common YAML errors:
- Missing closing `---`
- Incorrect indentation
- Unquoted special characters

#### Solution 3: Verify File Permissions
```bash
# Check permissions
ls -la skills/ agents/

# Fix if needed
chmod 755 skills/ agents/
chmod 644 skills/*/SKILL.md agents/*/SKILL.md
```

---

## Command Execution Fails

### Symptoms
- Command starts but fails with error
- "Tool not allowed" errors
- Permission denied

### Diagnosis

```bash
# 1. Check command definition
cat skills/cmd-{command-name}/SKILL.md

# 2. Verify allowed-tools
grep "allowed-tools:" skills/cmd-{command-name}/SKILL.md

# 3. Check recent logs
tail -f ~/.ccc/logs/debug.log
```

### Solutions

#### Solution 1: Check Tool Permissions

**Problem**: Tool not in `allowed-tools` list

```yaml
# Before (missing Write)
allowed-tools:
  - Read
  - Grep

# After
allowed-tools:
  - Read
  - Grep
  - Write  # Added
```

#### Solution 2: Verify SubAgent permissions

**Problem**: SubAgent missing `permissionMode`

```yaml
# Before
tools:
  - Bash
  - Write

# After
tools:
  - Bash
  - Write
permissionMode: prompt  # Added
```

#### Solution 3: Check Hook Blockers

```bash
# Disable hooks temporarily to test
export CCC_ENABLE_HOOKS=0

# Run command
/ccc:your-command

# Re-enable hooks
export CCC_ENABLE_HOOKS=1
```

---

## Review Issues

### Review Fails with Low Score

#### Symptoms
- `/ccc:review` shows many errors
- Score below threshold (default 80)
- Unexpected warnings

#### Diagnosis

```bash
# Run review with verbose output
/ccc:review . --verbose

# Check specific rule
grep -A20 "RULE-ID" docs/reviews/latest-review.md
```

#### Solutions

##### Solution 1: Read Review Report Carefully
```bash
# Review generates detailed report
cat docs/reviews/$(ls -t docs/reviews/*.md | head -1)
```

Focus on:
1. **ERROR** level issues first
2. Check official documentation references
3. Review suggested fixes

##### Solution 2: Use Fix Command
```bash
# Auto-fix some issues
/ccc:fix --report docs/reviews/latest-review.md

# For interactive fixes
/ccc:fix --interactive
```

##### Solution 3: Check Rule Accuracy
```bash
# If rule seems incorrect, check against official docs
grep -A10 "official_reference" agents/reviewer/knowledge/antipatterns/{category}/{rule}.yaml
```

### Review Takes Too Long

#### Solutions

##### Solution 1: Reduce Scope
```bash
# Review specific component instead of entire project
/ccc:review skills/cmd-review/

# Review specific type
/ccc:review agents/ --type subagent
```

##### Solution 2: Disable Expensive Checks
```bash
# Skip architecture analysis
/ccc:review . --no-arch

# Reduce parallel agents
export CCC_MAX_PARALLEL_AGENTS=1
```

##### Solution 3: Clear Cache
```bash
# Clear stale cache
rm -rf .ccc/cache/
```

---

## Artifacts Not Found

### Symptoms
- "Intent/Blueprint not found" errors
- `/ccc:status` shows no artifacts
- Workflow commands fail

### Diagnosis

```bash
# 1. Check artifacts directory
ls -la .ccc/artifacts/

# 2. Verify artifact files
find .ccc/artifacts/ -name "*.yaml"

# 3. Check permissions
ls -l .ccc/artifacts/*.yaml
```

### Solutions

#### Solution 1: Verify Artifacts Directory
```bash
# Check if directory exists
if [ ! -d ".ccc/artifacts" ]; then
  mkdir -p .ccc/artifacts/.metadata
  echo "Created artifacts directory"
fi
```

#### Solution 2: Check Artifact Format
```yaml
# Valid artifact must have:
id: intent-001
type: intent
# ... other fields
```

#### Solution 3: Use Status Command
```bash
# Check all artifacts
/ccc:status

# Check specific artifact
/ccc:status --artifact-id intent-001
```

#### Solution 4: Regenerate Missing Artifacts
```bash
# If intent is missing
/ccc:init

# If blueprint is missing
/ccc:design
```

---

## Permission Errors

### Symptoms
- "Permission denied" errors
- Hooks fail to execute
- SubAgents can't access files

### Diagnosis

```bash
# 1. Check file permissions
ls -la .

# 2. Check hook script permissions
ls -la hooks/scripts/

# 3. Verify SubAgent permissions
grep -A5 "permissionMode:" agents/*/SKILL.md
```

### Solutions

#### Solution 1: Fix Script Permissions
```bash
# Make hook scripts executable
chmod +x hooks/scripts/*.sh

# Verify
ls -l hooks/scripts/
```

#### Solution 2: Set permissionMode Correctly
```yaml
# For sensitive operations
tools:
  - Bash
  - Write
permissionMode: prompt  # User confirms each action
```

#### Solution 3: Check Directory Permissions
```bash
# Ensure readable/writable
chmod 755 .ccc/
chmod 755 .ccc/artifacts/
chmod 644 .ccc/artifacts/*.yaml
```

---

## Model/Token Issues

### Context Too Long

#### Symptoms
- "Context too long" errors
- "Token limit exceeded"
- Slow performance

#### Solutions

##### Solution 1: Use Efficient Models
```yaml
# Use haiku for simple tasks
model: haiku  # Instead of sonnet

# In SubAgent frontmatter
model: inherit  # Use user's model choice
```

##### Solution 2: Reduce Description Length
```yaml
# Before (too long)
description: "This component performs comprehensive analysis..."

# After (concise)
description: "Analyze components for quality issues. Use when: review needed."
```

##### Solution 3: Split Large Components
```bash
# Instead of one large SubAgent
agents/large-agent/

# Split into focused SubAgents
agents/analyzer/
agents/reporter/
agents/validator/
```

##### Solution 4: Adjust Token Budget
```bash
# Increase if needed (use cautiously)
export SLASH_COMMAND_TOOL_CHAR_BUDGET=20000

# Default is 16000
```

### Model Not Available

#### Symptoms
- "Model not found" errors
- Specified model doesn't exist

#### Solutions

```yaml
# Use valid model names
model: sonnet   # ✅
model: opus     # ✅
model: haiku    # ✅
model: inherit  # ✅ (recommended)

model: gpt-4    # ❌ Invalid
```

---

## Platform-Specific Issues

### Windows (WSL)

#### Issue: Path Separators
```bash
# ❌ Wrong
path = "C:\Users\name\file.txt"

# ✅ Correct (use forward slashes)
path = "/mnt/c/Users/name/file.txt"
```

#### Issue: Line Endings
```bash
# Convert CRLF to LF
dos2unix hooks/scripts/*.sh
# or
sed -i 's/\r$//' hooks/scripts/*.sh
```

#### Issue: Script Execution
```bash
# Ensure scripts have proper shebang
#!/bin/bash
# (not #!/usr/bin/env bash on some WSL setups)
```

### macOS

#### Issue: Permission Dialogs
```bash
# Grant permissions in System Preferences > Security & Privacy
# Allow Claude Code to access:
# - Files and Folders
# - Full Disk Access (if needed)
```

#### Issue: Quarantine Attributes
```bash
# Remove quarantine from downloaded files
xattr -r -d com.apple.quarantine hooks/scripts/

# Verify
ls -l@ hooks/scripts/
```

#### Issue: Bash vs Zsh
```bash
# Ensure scripts use correct shell
#!/bin/bash  # Explicit bash
# or
#!/bin/zsh   # For zsh-specific features
```

### Linux

#### Issue: SELinux/AppArmor
```bash
# Check SELinux status
sestatus

# If enforcing, may need to adjust policies
# (Consult SELinux documentation)
```

#### Issue: User Permissions
```bash
# Ensure user can execute scripts
chmod u+x hooks/scripts/*.sh

# Check ownership
ls -l hooks/scripts/
```

---

## Performance Issues

### CCC is Slow

#### Diagnosis
```bash
# Enable debug logging
export CCC_DEBUG=1
export CCC_LOG_LEVEL=debug

# Run command and check logs
/ccc:review .
tail -f ~/.ccc/logs/debug.log
```

#### Solutions

##### Solution 1: Reduce Review Scope
```bash
# Review specific paths
/ccc:review skills/cmd-review/ --no-arch
```

##### Solution 2: Limit Parallel Execution
```bash
# Reduce concurrent agents (may use less memory but take longer)
export CCC_MAX_PARALLEL_AGENTS=1
```

##### Solution 3: Use Faster Models
```yaml
# For non-critical SubAgents
model: haiku  # Faster than sonnet/opus
```

##### Solution 4: Clear Cache
```bash
# Remove stale cache
rm -rf .ccc/cache/
```

##### Solution 5: Disable Hooks Temporarily
```bash
# If hooks are slow
export CCC_ENABLE_HOOKS=0
```

---

## Hook Issues

### Hook Not Executing

#### Diagnosis
```bash
# 1. Check hooks configuration
cat hooks/hooks.json | jq .

# 2. Verify script exists
ls -la hooks/scripts/

# 3. Test script manually
export TOOL_NAME="Bash"
export TOOL_ARGS='{"command": "ls"}'
hooks/scripts/security-check.sh
echo $?  # Should be 0, 1, or 2
```

#### Solutions

##### Solution 1: Verify Configuration
```json
{
  "hooks": [
    {
      "event": "PreToolUse",           // Correct event name
      "script": "hooks/scripts/...",   // Correct path
      "timeout": 5000                  // Reasonable timeout
    }
  ]
}
```

##### Solution 2: Fix Script Errors
```bash
# Check script syntax
bash -n hooks/scripts/security-check.sh

# Run with debugging
bash -x hooks/scripts/security-check.sh
```

##### Solution 3: Check Event Names
Valid events:
- `PreToolUse`
- `PostToolUse`
- `UserPromptSubmit`
- `SubagentStart`
- `SubagentStop`
- `PermissionRequest`

### Hook Times Out

#### Solutions

```json
{
  "timeout": 10000  // Increase timeout (milliseconds)
}
```

```bash
# Optimize hook script for speed
# - Avoid expensive operations
# - Use early exit for fast paths
# - Cache results if possible
```

---

## Debug Mode

### Enable Debugging

```bash
# Environment variables
export CCC_DEBUG=1
export CCC_LOG_LEVEL=debug

# Run command
/ccc:your-command
```

### Check Logs

```bash
# View live logs
tail -f ~/.ccc/logs/debug.log

# Search logs
grep "ERROR" ~/.ccc/logs/debug.log

# View last 100 lines
tail -100 ~/.ccc/logs/debug.log
```

### Log Levels

| Level | Use | Example |
|-------|-----|---------|
| `debug` | Detailed info | Variable values, function calls |
| `info` | General info | Command start/end, major steps |
| `warn` | Warnings | Deprecated usage, non-fatal issues |
| `error` | Errors | Failures, exceptions |

---

## Getting Help

### Before Asking for Help

1. **Check this guide** for similar issues
2. **Run diagnostics**:
   ```bash
   /ccc:review .
   /ccc:status
   /ccc:validate
   ```
3. **Collect information**:
   - CCC version
   - Claude Code version
   - Operating system
   - Error messages
   - Steps to reproduce

### How to Report Issues

Create a GitHub issue with:

```markdown
## Environment
- OS: macOS 13.0 / Ubuntu 22.04 / Windows 11 WSL
- CCC Version: 3.0.0
- Claude Code Version: 0.1.5

## Problem Description
Brief description of the issue...

## Steps to Reproduce
1. Run `/ccc:command`
2. Error occurs at step X
3. Expected: Y, Actual: Z

## Error Messages
```
Paste error messages here
```

## Diagnostic Output
```bash
$ /ccc:status
... output ...
```

## Additional Context
Any other relevant information...
```

### Quick Diagnostic Commands

```bash
# Check CCC version
cat .claude-plugin/config.json | jq .version

# Verify configuration
cat .claude-plugin/config.json | jq .

# Check artifacts
/ccc:status

# Validate setup
/ccc:validate

# Run review
/ccc:review .

# Check hooks
cat hooks/hooks.json | jq .

# View environment
env | grep CCC_
```

---

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Tool not allowed" | Tool not in allowed-tools | Add tool to frontmatter |
| "Permission denied" | File/script not executable | `chmod +x` the file |
| "Artifact not found" | Missing/invalid artifact | Run `/ccc:status`, regenerate if needed |
| "Context too long" | Token limit exceeded | Use haiku model, reduce description length |
| "Hook timed out" | Hook script too slow | Increase timeout or optimize script |
| "Invalid YAML" | Syntax error in frontmatter | Check YAML syntax, indentation |
| "Model not found" | Invalid model name | Use sonnet/opus/haiku/inherit |
| "Review failed" | Component has errors | Read review report, fix issues |

---

## Preventive Maintenance

### Regular Checks

```bash
# Weekly: Run self-review
/ccc:review .

# Monthly: Clear old cache
rm -rf .ccc/cache/

# After updates: Validate configuration
/ccc:validate
```

### Best Practices

1. **Keep CCC updated**: `git pull origin main`
2. **Backup artifacts**: Commit `.ccc/artifacts/` to git
3. **Document customizations**: Comment configuration changes
4. **Test after changes**: Run `/ccc:review .` after modifying components
5. **Use version control**: Track all configuration files

---

## Resources

- [Configuration Guide](CONFIGURATION.md)
- [Permissions Documentation](docs/PERMISSIONS.md)
- [Security Policy](SECURITY.md)
- [Hooks Documentation](hooks/README.md)
- [GitHub Issues](https://github.com/mzdbxqh/claude-code-component-creator/issues)

---

**Still having issues?**

Create an issue on GitHub with diagnostic output and we'll help troubleshoot.

**Last Updated**: 2026-03-11
**Version**: 1.0.0
