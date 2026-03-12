---
name: cmd-diff
model: sonnet
context: fork
disable-model-invocation: true
allowed-tools: [Read, Glob, Grep]
description: "对比两个制品版本的差异。触发：对比/差异/变更。输出增删改的差异报告。"
argument-hint: "[--from=id] [--to=id] [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:diff

Compares differences between two artifact versions including intents, blueprints, and deliveries with detailed change summaries and export capabilities.

## 模型要求

- **推荐**: Claude Sonnet 4.5+ (高效能,最佳性价比)
- **可用**: Claude Haiku 3.5+ (快速推理,适用于简单对比)
- **最小**: Claude Haiku 3.5+ (最低要求)

### 功能需求
- 需要支持 Tool Use (Read, Glob, Grep)
- 需要支持多轮对话
- 建议上下文窗口 >= 100K tokens

## SubAgents 协作

本工作流使用以下 SubAgents 进行任务执行：

### 核心 Agents
本 skill 主要使用文件读取和差异对比，不需要专门的 SubAgent。直接使用 Read, Glob, Grep 工具完成。

### 调度策略
- **串行执行**: cmd-diff → 读取两个制品 → 对比差异 → 生成报告
- **并行执行**: 无（差异对比为简单操作）
- **错误处理**: 制品不存在时提示用户确认 ID；制品类型不匹配时报错

### 调用示例
```
用户: /ccc:diff --from=BLP-001 --to=BLP-002
  ↓
cmd-diff 读取两个 Blueprint 制品:
  - docs/ccc/blueprint/*-BLP-001.yaml
  - docs/ccc/blueprint/*-BLP-002.yaml
  ↓
对比差异:
  - 新增元素 (Added)
  - 修改元素 (Modified)
  - 删除元素 (Removed)
  ↓
生成差异报告
```

## Usage

```bash
/ccc:diff --from=BLP-001 --to=BLP-002
/ccc:diff --from=INT-001 --to=current
/ccc:diff --from=BLP-001 --to=BLP-002 --lang=en-us
```

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |

## Output Specification

### Console Output

```
Diff: BLP-001 → BLP-002

Added:
  + rollback configuration
  + multi-env support

Modified:
  ~ deployment strategy: sequential → parallel

Removed:
  - deprecated field: legacy_trigger
```

### File Output

| Attribute | Value |
|-----------|-------|
| **Directory** | `docs/ccc/diffs/` |
| **Filename** | `YYYY-MM-DD-<artifact-id>-diff.md` |
| **Format** | Markdown |
| **Overwrite** | No (timestamp ensures uniqueness) |

**Example:**
- `/ccc:diff --from=BLP-001 --to=BLP-002` → `docs/ccc/diffs/2026-03-02-BLP-001-diff.md`

### Report Structure

| Section | Content |
|---------|---------|
| Overview | Source and target artifacts, diff date |
| Added Elements | New items in target version |
| Modified Elements | Changed items between versions |
| Removed Elements | Deleted items from source version |
| Summary | Statistics and change impact |

### Export Options

| Option | Description |
|--------|-------------|
| `--export=json` | Export diff as JSON for programmatic processing |
| `--export=md` | Export as Markdown report (default) |

### File Access

```bash
# View the generated diff report
cat docs/ccc/diffs/YYYY-MM-DD-<artifact-id>-diff.md

# List all diff reports
ls -la docs/ccc/diffs/
```

## Error Handling

### Common Errors

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `DIFF-001` | Source artifact not found | Verify artifact ID exists |
| `DIFF-002` | Target artifact not found | Verify artifact ID exists |
| `DIFF-003` | No differences detected | Artifacts may be identical |
| `DIFF-004` | Unsupported artifact type | Check artifact type compatibility |

### Error Messages

```
❌ Error: Source artifact 'BLP-999' not found
   → Use '/ccc:list' to see available artifacts

❌ Error: Target artifact 'DLV-999' not found
   → Use '/ccc:list' to see available artifacts

❌ Error: No differences between INT-001 and INT-002
   → Artifacts may be identical or have same content

❌ Error: Cannot diff 'INTENT' with 'DELIVERY' types
   → Only diff same artifact types (Intent↔Intent, Blueprint↔Blueprint, etc.)
```

### Recovery Steps

1. **List artifacts**: `/ccc:list --project-id=<id>`
2. **Check artifact details**: `/ccc:show --artifact-id=<id>`
3. **Compare with different targets**: `/ccc:diff --from=<id1> --to=<id2>`
4. **Export diff for analysis**: `/ccc:diff --from=<id1> --to=<id2> --export=diff.json`

## 使用示例 (Examples)

### Example 1: Blueprint 版本对比

```bash
/ccc:diff --from=BLP-001 --to=BLP-002
```

**输入**: 两个 Blueprint artifact ID

**输出**:
```
Diff: BLP-001 → BLP-002

Added:
  + rollback configuration
  + multi-env support

Modified:
  ~ deployment strategy: sequential → parallel

Removed:
  - deprecated field: legacy_trigger

Report saved to: docs/ccc/diffs/2026-03-11-BLP-001-diff.md
```

### Example 2: Intent 迭代对比（JSON 导出）

```bash
/ccc:diff --from=INT-001 --to=current --export=json
```

**输入**: 旧版本 Intent 和当前版本对比，导出 JSON 格式

**输出**:
- 控制台显示简要差异摘要
- 生成 JSON 文件：`docs/ccc/diffs/2026-03-11-INT-001-diff.json`，包含：
  - 新增需求列表
  - 修改的需求对比（before/after）
  - 删除的需求列表
  - 变更影响分析数据（用于程序化处理）

### Example 3: 跨制品类型差异分析（错误示例）

```bash
/ccc:diff --from=INT-001 --to=BLP-001
```

**输入**: 尝试对比不同类型的制品

**输出**: 错误提示
```
❌ Error: Cannot diff 'INTENT' with 'BLUEPRINT' types
   → Only diff same artifact types (Intent↔Intent, Blueprint↔Blueprint, etc.)

Suggestion:
   - Compare Intent versions: /ccc:diff --from=INT-001 --to=INT-002
   - Compare Blueprint versions: /ccc:diff --from=BLP-001 --to=BLP-002
```
