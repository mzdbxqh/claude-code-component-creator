---
name: ccc:cmd-status-graph
model: sonnet
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
description: "Generates visual ASCII dependency graph of all artifacts in project showing relationships between intents, blueprints, and deliveries with status indicators"
argument-hint: "[--project-id=current] [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:status-graph

Shows ASCII/text graph of artifact dependencies.

## Usage

```bash
# Basic usage - show graph for current project
/ccc:status-graph

# Show graph for specific project
/ccc:status-graph --project-id=my-project

# Simplified ASCII graph (faster)
/ccc:status-graph --simple

# Export graph to JSON file
/ccc:status-graph --export=graph.json

# Show only completed artifacts
/ccc:status-graph --filter=completed

# Show graph with depth limit
/ccc:status-graph --max-depth=3

# Show graph in English
/ccc:status-graph --lang=en-us
```

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |

## Examples

### Example 1: Basic Project Graph
```bash
/ccc:status-graph --project-id=web-app
```
```
Project: web-app

Intent: INT-001 (User Authentication)
    │
    ▼
Blueprint: BLP-001 (Auth Flow)
    │
    ├─▶ Delivery: DLV-001 (Login Component) [completed]
    │
    └─▶ Blueprint: BLP-002 (Session Management) [in_progress]
         │
         ▼
    Delivery: DLV-002 (Session Handler) [pending]
```

### Example 2: Simplified View
```bash
/ccc:status-graph --project-id=data-pipeline --simple
```
```
data-pipeline
├── INT-001 → BLP-001 → DLV-001 ✓
├── INT-002 → BLP-002 → DLV-002 →
└── INT-003 → BLP-003 → DLV-003 ⏳
```

### Example 3: Filtered by Status
```bash
/ccc:status-graph --project-id=api-gateway --filter=in_progress
```
```
Project: api-gateway (in_progress only)

Blueprint: BLP-004 (Rate Limiting)
    │
    ▼
Delivery: DLV-004 (Rate Limiter) [in_progress]

Blueprint: BLP-005 (Circuit Breaker)
    │
    ▼
Delivery: DLV-005 (Circuit Breaker) [in_progress]
```

## Output Specification

### Console Output

```
Project: web-app

Intent: INT-001 (User Authentication)
    │
    ▼
Blueprint: BLP-001 (Auth Flow)
    │
    ├─▶ Delivery: DLV-001 (Login Component) [completed]
    │
    └─▶ Blueprint: BLP-002 (Session Management) [in_progress]
         │
         ▼
    Delivery: DLV-002 (Session Handler) [pending]
```

### File Output

| Attribute | Value |
|-----------|-------|
| **Directory** | `docs/ccc/graphs/` |
| **Filename** | `YYYY-MM-DD-<project-id>-graph.md` |
| **Format** | Markdown |
| **Overwrite** | Yes (updated on each graph generation) |

**Example:**
- `/ccc:status-graph --project-id=web-app` → `docs/ccc/graphs/web-app-graph.md`

### Export Options

| Option | Description |
|--------|-------------|
| `--export=json` | Export graph as JSON for programmatic processing |
| `--simple` | Simplified ASCII graph format |
| `--filter=completed` | Show only completed artifacts |

### Graph Structure

| Element | Representation |
|---------|---------------|
| Intent | Root node with requirement summary |
| Blueprint | Child node linked to Intent |
| Delivery | Leaf node linked to Blueprint |
| Status | Indicator: [completed], [in_progress], [pending] |

### File Access

```bash
# View the generated graph
cat docs/ccc/graphs/<project-id>-graph.md

# List all graph reports
ls -la docs/ccc/graphs/
```

## Error Handling

### Common Errors

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `GRAPH-001` | No artifacts found | Run `/ccc:init` to create first artifact |
| `GRAPH-002` | Invalid project ID | Use `/ccc:status` to list valid project IDs |
| `GRAPH-003` | Graph generation timeout | Reduce graph complexity or use `--simple` flag |

### Error Messages

```
❌ Error: No artifacts found in project 'my-project'
   → Run '/ccc:init' to create your first artifact

❌ Error: Invalid project ID 'invalid-id'
   → Use '/ccc:status' to list available projects

❌ Error: Graph generation timeout (exceeded 30s)
   → Try '/ccc:status-graph --simple' for simplified view
```

### Recovery Steps

1. **Verify project exists**: `/ccc:status --project-id=<id>`
2. **Check artifact count**: `/ccc:list --project-id=<id>`
3. **Generate simple graph**: `/ccc:status-graph --simple`
4. **Export for debugging**: `/ccc:status-graph --export=debug.json`
