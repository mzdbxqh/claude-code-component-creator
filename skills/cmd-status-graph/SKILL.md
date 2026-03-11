---
name: ccc:cmd-status-graph
model: sonnet
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
description: "依赖关系图 | 场景: 独立工具"
argument-hint: "[--project-id=current] [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:status-graph

Generates visual ASCII dependency graph of all artifacts in project showing relationships between intents, blueprints, and deliveries with status indicators.

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

### Example 4: 复杂依赖关系图

```bash
/ccc:status-graph --project-id=microservices --max-depth=5
```

**输入**: 微服务架构项目，最大深度5层

**输出**:
```
Project: microservices

Intent: INT-001 (API Gateway)
    │
    ▼
Blueprint: BLP-001 (Gateway Core)
    │
    ├─▶ Delivery: DLV-001 (Gateway Service) [completed] ✓
    │
    └─▶ Blueprint: BLP-002 (Auth Module)
         │
         ├─▶ Delivery: DLV-002 (JWT Handler) [completed] ✓
         │
         └─▶ Blueprint: BLP-003 (OAuth Integration)
              │
              └─▶ Delivery: DLV-003 (OAuth Client) [in_progress] ⏳

Intent: INT-002 (Service Mesh)
    │
    ▼
Blueprint: BLP-004 (Istio Config)
    │
    └─▶ Delivery: DLV-004 (Mesh Setup) [pending] →

Graph saved to: docs/ccc/graphs/microservices-graph.md
```

### Example 5: 导出 JSON 格式

```bash
/ccc:status-graph --export=graph.json
```

**输入**: 当前项目，导出 JSON 格式

**输出**:
- 控制台显示简化的文本图
- 生成 JSON 文件：`graph.json`，包含：
```json
{
  "project": "current-project",
  "nodes": [
    {"id": "INT-001", "type": "intent", "label": "User Authentication"},
    {"id": "BLP-001", "type": "blueprint", "label": "Auth Flow"},
    {"id": "DLV-001", "type": "delivery", "label": "Login Component", "status": "completed"}
  ],
  "edges": [
    {"from": "INT-001", "to": "BLP-001"},
    {"from": "BLP-001", "to": "DLV-001"}
  ]
}
```
- 可用于程序化处理或可视化工具导入

### Example 6: 边界情况 - 空项目

```bash
/ccc:status-graph --project-id=new-project
```

**输入**: 新创建的空项目

**输出**:
```
❌ Error: No artifacts found in project 'new-project'
   → Run '/ccc:init' to create your first artifact

Suggestions:
  1. Create an Intent: /ccc:init --type=intent
  2. Or import existing project: /ccc:import --from=template
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

## Workflow

### Step 1: Load Project Artifacts
**目标**: 加载项目的所有制品
**操作**: 扫描并读取 Intent、Blueprint、Delivery 制品
**输出**: 制品数据集合
**错误处理**: 项目不存在时提示运行 /ccc:status 查看可用项目；无制品时提示运行 /ccc:init 创建首个制品

### Step 2: Build Dependency Graph
**目标**: 构建依赖关系图
**操作**: 分析制品间的链接关系
**输出**: 依赖图数据结构
**错误处理**: 依赖链断裂时标记为部分关系并在图中显示警告；循环依赖时记录错误并尝试打破循环显示

### Step 3: Generate ASCII Visualization
**目标**: 生成 ASCII 可视化图
**操作**: 将依赖图渲染为文本格式
**输出**: ASCII 格式的依赖图
**错误处理**: 图生成超时（>30秒）时提示使用 --simple 标志简化视图；图过于复杂时自动切换为简化模式并提示用户

### Step 4: Output and Save
**目标**: 输出并保存图形
**操作**: 显示到控制台并保存到文件
**输出**: 控制台输出和图形文件
**错误处理**: 文件保存失败时仅显示到控制台并提示权限问题；目录不存在时自动创建 docs/ccc/graphs/

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
