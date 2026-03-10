---
name: ccc:cmd-quick
model: sonnet
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
description: "Executes complete workflow from intent to delivery in a single command with auto-approval options"
argument-hint: "<requirement-description> [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:quick

Runs full workflow: init → design → build in sequence.

## Usage

```bash
/ccc:quick "我要做一个自动部署工具，支持 Kubernetes"
/ccc:quick "I want to create an auto-deployment tool with Kubernetes support" --lang=en-us
```

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |

## Workflow

1. Run `/ccc:init` with description
2. Auto-approve Intent
3. Run `/ccc:design`
4. Auto-approve Blueprint if quality > 85
5. Run `/ccc:build`
6. Show final Delivery summary

## Output Specification

### Console Output (渐进式输出)

**阶段 1 - Intent 完成**:
```
┌─────────────────────────────────────────────────────┐
│ 📋 Stage 1: Intent Creation ✓ COMPLETED            │
├─────────────────────────────────────────────────────┤
│ ID: INT-2026-03-07-001                              │
│ Quality: 89/100  [█████████████████░░] 优秀         │
│                                                     │
│ 核心目标：快速查找项目中的 TODO 注释                  │
│ 组件类型：Skill                                     │
│ 复杂度：simple                                      │
└─────────────────────────────────────────────────────┘
                    ↓
```

**阶段 2 - Blueprint 完成**:
```
┌─────────────────────────────────────────────────────┐
│ 📐 Stage 2: Blueprint Design ✓ COMPLETED           │
├─────────────────────────────────────────────────────┤
│ ID: BLP-2026-03-07-001                              │
│ Quality: 92/100  [██████████████████░] 优秀         │
│ Status: ✓ Auto-approved (质量 > 85)                 │
│                                                     │
│ 架构模式：Search-Filter-Sort                        │
│ 工具：Read, Grep                                    │
│ 估算时间：30 分钟                                     │
└─────────────────────────────────────────────────────┘
                    ↓
```

**阶段 3 - Delivery 完成**:
```
┌─────────────────────────────────────────────────────┐
│ 📦 Stage 3: Delivery ✓ COMPLETED                   │
├─────────────────────────────────────────────────────┤
│ ID: DLV-2026-03-07-001                              │
│ Compliance: 88/100  [████████████████░░] 良好       │
│                                                     │
│ 生成文件：                                          │
│   ✓ SKILL.md (156 行)                               │
│   ✓ README.md                                       │
│   ✓ metadata.yaml                                   │
│   ✓ tests/evals.json           【新增测试框架】     │
│   ✓ tests/README.md            【新增测试指南】     │
│   ✓ tests/fixtures/            【新增测试夹具】     │
└─────────────────────────────────────────────────────┘
```

**最终汇总**:
```
🚀 Quick Workflow Complete!

┌─────────────────────────────────────────────────────┐
│ 全流程摘要                                          │
├─────────────────────────────────────────────────────┤
│ Intent    →  Blueprint   →  Delivery               │
│ 89/100 ✓     92/100 ✓      88/100 ✓                │
│                                                     │
│ 总耗时：4 分 32 秒                                    │
│ 生成文件：3 个                                       │
│ 状态：✅ 通过 (所有阶段质量达标)                      │
└─────────────────────────────────────────────────────┘

📄 Generated Files:
   ├─ docs/ccc/intent/INT-2026-03-07-001.yaml
   ├─ docs/ccc/blueprint/BLP-2026-03-07-001.yaml
   └─ docs/ccc/delivery/DLV-2026-03-07-001/SKILL.md

Next steps:
   1. 📖 Review the generated SKILL.md
   2. 🔍 Run /ccc:review for detailed analysis
   3. 🔄 Iterate if needed with /ccc:iterate
```

### File Outputs

| Artifact | Directory | Filename | Format |
|----------|-----------|----------|--------|
| **Intent** | `docs/ccc/intent/` | `YYYY-MM-DD-<artifact-id>.yaml` | YAML |
| **Blueprint** | `docs/ccc/blueprint/` | `YYYY-MM-DD-<artifact-id>.yaml` | YAML |
| **Delivery** | `docs/ccc/delivery/<artifact-id>/` | `SKILL.md`, `README.md`, `metadata.yaml`, `tests/`, `implementation/` | Mixed |

### File Access

```bash
# View intent artifact
cat docs/ccc/intent/YYYY-MM-DD-INT-*.yaml

# View blueprint artifact
cat docs/ccc/blueprint/YYYY-MM-DD-BLP-*.yaml

# View delivery SKILL.md
cat docs/ccc/delivery/YYYY-MM-DD-DLV-*/SKILL.md

# List all generated files
ls -la docs/ccc/delivery/YYYY-MM-DD-DLV-*/
```

## Options

```bash
/ccc:quick "description" --auto-approve    # Auto-approve all stages
/ccc:quick "description" --stop-at=blueprint  # Stop after Blueprint
/ccc:quick "description" --lang=en-us     # English output
```

## Error Handling

| Error Scenario | Handling Strategy | 用户可见消息 |
|----------------|-------------------|-------------|
| Empty description | Prompt user for requirement description | "请提供您想要创建的技能描述。例如：'我想要一个技能来快速查找项目中的 TODO 注释'" |
| Intent generation fails | Display error, suggest rephrasing | "Intent 生成失败：{error}。请尝试重新描述您的需求，或将其分解为更小的功能点" |
| Blueprint quality below threshold | Pause for manual review before continuing | "Blueprint 质量 {score}/100 低于阈值 85。建议：1. 使用 /ccc:iterate 改进设计 2. 手动审查后继续" |
| Build generation fails | Display error with artifact ID for manual iteration | "Delivery 生成失败：{error}。请使用 /ccc:build --artifact-id={id} 手动重试，或联系开发者" |
| Stage timeout | Report timeout, provide command to resume from that stage | "阶段超时（>{timeout}）。已保存进度，使用 /ccc:design --intent-id={id} 从该阶段继续" |
| File write permission denied | Suggest checking directory permissions | "无法写入文件：{path}。请检查目录权限，或使用 --output-dir 指定其他输出目录" |
| Invalid artifact ID | List available artifact IDs | "找不到工件：{id}。使用 /ccc:status 查看可用的工件列表" |
