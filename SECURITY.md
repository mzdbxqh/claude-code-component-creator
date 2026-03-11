# Security Policy

## Overview

CCC (Claude Code Component Creator) takes security seriously. This document outlines security considerations, best practices, and reporting procedures.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 3.0.x   | :white_check_mark: |
| < 3.0   | :x:                |

## Security Features

### 1. Permission System

CCC implements a comprehensive permission system following the principle of least privilege:

**Skills** use `allowed-tools`:
```yaml
allowed-tools:
  - Read
  - Grep
  - Glob
```

**SubAgents** use `tools` with `permissionMode`:
```yaml
tools:
  - Read
  - Write
permissionMode: prompt  # User confirmation required
```

See [PERMISSIONS.md](docs/PERMISSIONS.md) for details.

### 2. Hooks for Security Validation

CCC supports PreToolUse hooks for security checks:

```json
{
  "event": "PreToolUse",
  "matcher": {"tool": "Bash"},
  "script": "hooks/scripts/security-check.sh"
}
```

The security-check hook detects:
- Dangerous commands (`rm -rf /`, `dd`, `mkfs`)
- Sensitive file modifications (`/etc/`, `.ssh/`, credentials)
- Suspicious patterns

### 3. Input Validation

All CCC components validate inputs:
- Path traversal prevention
- Command injection protection
- File type validation
- Size limits enforcement

### 4. Sandboxing

SubAgents can run in isolated contexts:
- `context: fork` - Isolated execution environment
- `context: main` - Shared context (use with caution)

## Security Best Practices

### For Plugin Developers

#### 1. Use Minimum Necessary Permissions

❌ **Bad**: Excessive permissions
```yaml
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - WebFetch
```

✅ **Good**: Only necessary tools
```yaml
allowed-tools:
  - Read
  - Grep
```

#### 2. Always Use permissionMode for Sensitive Operations

❌ **Bad**: Auto-grant sensitive permissions
```yaml
tools:
  - Bash
  - Write
permissionMode: auto  # Dangerous!
```

✅ **Good**: Require user confirmation
```yaml
tools:
  - Bash
  - Write
permissionMode: prompt
```

#### 3. Validate All External Input

```python
# ❌ Bad: Direct use of user input
bash_tool(f"ls {user_path}")

# ✅ Good: Validate and sanitize
if is_valid_path(user_path) and not contains_dangerous_chars(user_path):
    bash_tool(f"ls {shlex.quote(user_path)}")
else:
    raise ValueError("Invalid path")
```

#### 4. Never Store Secrets in Code

❌ **Bad**: Hardcoded secrets
```yaml
api_key: "sk-1234567890abcdef"  # Never do this!
```

✅ **Good**: Use environment variables
```yaml
# Reference environment variable
api_key: "${API_KEY}"
```

#### 5. Implement Proper Error Handling

```yaml
# Don't expose sensitive information in errors
error_handling:
  - Log errors securely
  - Return generic error messages to users
  - Never include stack traces with sensitive data
```

### For Plugin Users

#### 1. Review Permissions Before Installation

Check `allowed-tools` and `tools` declarations:
```bash
# Review permissions
grep -A5 "allowed-tools:\|^tools:" skills/*/SKILL.md agents/*/SKILL.md
```

#### 2. Use Hooks for Additional Protection

Configure security hooks in `hooks/hooks.json`:
```json
{
  "hooks": [
    {
      "event": "PreToolUse",
      "matcher": {"tool": "Bash"},
      "script": "hooks/scripts/security-check.sh"
    }
  ]
}
```

#### 3. Regular Security Audits

Run CCC review to check for security issues:
```bash
/ccc:review .
```

Look for:
- PERM-001: Excessive permissions
- PERM-002: Permission inconsistency
- PERM-003: Permission syntax errors
- PERM-004: Unprotected sensitive tools
- SEC-*: Other security issues

#### 4. Keep CCC Updated

```bash
# Check for updates
git pull origin main

# Verify no security issues
/ccc:review .
```

## Known Security Considerations

### 1. Bash Tool Risks

The `Bash` tool can execute arbitrary commands:
- **Mitigation**: Always use `permissionMode: prompt`
- **Mitigation**: Implement security hooks
- **Mitigation**: Validate all command inputs

### 2. File Write Risks

`Write` and `Edit` tools can modify files:
- **Mitigation**: Use `permissionMode: prompt`
- **Mitigation**: Validate file paths
- **Mitigation**: Implement backups before modifications

### 3. WebFetch Risks

Fetching external content can expose data:
- **Mitigation**: Validate URLs
- **Mitigation**: Use HTTPS only
- **Mitigation**: Sanitize fetched content

### 4. Environment Variable Exposure

Environment variables may contain secrets:
- **Mitigation**: Never log environment variables
- **Mitigation**: Use specific variable names (not wildcard access)
- **Mitigation**: Document required environment variables

## Security Antipatterns

CCC includes security antipattern detection:

| Rule | Severity | Description |
|------|----------|-------------|
| PERM-001 | Error | Excessive permissions (violates least privilege) |
| PERM-002 | Error | Permission declaration inconsistent with usage |
| PERM-003 | Error | Permission configuration syntax error |
| PERM-004 | Warning | Sensitive tools without permission protection |
| SEC-001 | Error | Missing permissionMode for SubAgents |
| SEC-002 | Warning | Hardcoded credentials detected |
| SEC-003 | Warning | Unsafe command construction |
| SEC-004 | Warning | Missing input validation |
| SEC-005 | Info | Overly broad file access patterns |

## Vulnerability Reporting

### Reporting Process

If you discover a security vulnerability:

1. **DO NOT** create a public GitHub issue
2. Email security details to: [maintainer email - to be added]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- **24 hours**: Initial acknowledgment
- **72 hours**: Preliminary assessment
- **7 days**: Detailed response with fix timeline
- **30 days**: Security patch release (for critical issues)

### Disclosure Policy

- We follow **responsible disclosure**
- Security fixes are released before public disclosure
- Credit given to reporters (unless anonymity requested)

## Security Checklist

### For New Components

- [ ] Minimum necessary permissions declared
- [ ] permissionMode set appropriately
- [ ] Input validation implemented
- [ ] Error handling doesn't leak sensitive data
- [ ] No hardcoded secrets
- [ ] Security hooks configured (if using Bash/Write/Edit)
- [ ] Reviewed with `/ccc:review`
- [ ] Tested with restricted permissions

### For Updates

- [ ] Permission changes reviewed
- [ ] New tools usage justified
- [ ] Security implications documented
- [ ] Regression tests passed
- [ ] Security review completed

## Compliance

CCC follows security standards from:
- **Claude Code Official Documentation**: permissions.md, security best practices
- **OWASP Top 10**: Protection against common vulnerabilities
- **Principle of Least Privilege**: Minimum necessary permissions
- **Defense in Depth**: Multiple security layers (permissions + hooks + validation)

## Resources

- [Permissions Documentation](docs/PERMISSIONS.md)
- [Hooks Configuration](hooks/README.md)
- [Security Antipatterns](agents/reviewer/knowledge/antipatterns/security/)
- [CCC Review Tool](/ccc:review)

## Updates

This security policy is reviewed and updated:
- After each major release
- When new security features are added
- When vulnerabilities are discovered
- At least quarterly

**Last Updated**: 2026-03-11
**Version**: 1.0.0

---

## Contact

For security concerns: [To be added]
For general questions: GitHub Issues

**Remember**: Security is a shared responsibility. Plugin developers and users must both follow security best practices.
