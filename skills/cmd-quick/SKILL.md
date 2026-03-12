---
name: cmd-quick
model: sonnet
context: fork
disable-model-invocation: true
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, Task]
description: "一键执行完整流程(init→design→build)。触发：快速/原型/一键。输出完整制品包。"
argument-hint: "<requirement-description> [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:quick

**等价流程**: **quick** ≈ `init` → `design` → `build`（自动化执行）

Executes complete workflow from intent to delivery in a single command with auto-approval options.

## 模型要求

- **推荐**: Claude Sonnet 4.5+ (高效能,最佳性价比)
- **可用**: Claude Opus 4.5+ (最高质量,完整流程)
- **最小**: Claude Sonnet 4.5+ (最低要求)

### 功能需求
- 需要支持 Tool Use (Bash, Read, Write, Edit, Glob, Grep, Task)
- 需要支持多轮对话和自动化流程
- 需要执行 init → design → build 完整流程
- 建议上下文窗口 >= 200K tokens (处理完整端到端流程)

## SubAgents 协作

本工作流使用以下 SubAgents 进行端到端任务执行：

### 核心 Agents
本 skill 是集成型命令，内部串行调用其他 cmd skills 完成工作流，使用的 SubAgents 包括：
- **ccc:intent-core**: 通过 cmd-init 调用，创建 Intent 制品
- **advisor-core, requirement-core, architect-core, blueprint-core**: 通过 cmd-design 调用，生成 Blueprint 制品
- **blueprint-core, delivery-core, checkpoint-core**: 通过 cmd-build 调用，生成 Delivery 制品

### 调度策略
- **串行执行**: cmd-quick → cmd-init → cmd-design → cmd-build
- **并行执行**: 无（端到端流程需按顺序执行）
- **错误处理**: 任何阶段失败时保存已完成的制品并提供继续执行的命令

### Agent 输入输出
| Stage | 输入 | 输出 |
|-------|------|------|
| cmd-init | 需求描述 | Intent 制品 |
| cmd-design | Intent 制品 | Blueprint 制品 |
| cmd-build | Blueprint 制品 | Delivery 制品 |

### 调用示例
```
用户: /ccc:quick "我要做一个自动部署工具"
  ↓
cmd-quick 启动端到端流程
  ↓
Step 1: 调用 cmd-init (创建 Intent)
  ↓ 自动批准 Intent
Step 2: 调用 cmd-design (生成 Blueprint)
  ↓ 自动批准 Blueprint
Step 3: 调用 cmd-build (生成 Delivery)
  ↓
cmd-quick 输出完整制品路径和摘要
```

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

### Step 1: Run /ccc:init
**目标**: 初始化 Intent 制品
**操作**: 使用用户描述创建 Intent
**输出**: Intent 制品（INT-xxx）
**错误处理**: 描述为空时提示用户提供需求描述；Intent 生成失败时显示错误并建议重新描述或分解需求

### Step 2: Auto-approve Intent
**目标**: 自动批准 Intent
**操作**: 验证 Intent 质量并自动批准
**输出**: 已批准的 Intent
**错误处理**: Intent 质量过低（<60分）时暂停并要求用户确认是否继续；验证失败时显示具体问题并提供修改建议

### Step 3: Run /ccc:design
**目标**: 生成 Blueprint 制品
**操作**: 基于 Intent 创建 Blueprint
**输出**: Blueprint 制品（BLP-xxx）
**错误处理**: Blueprint 生成失败时显示错误和 Intent ID 供手动重试；生成超时时保存进度并提供从该阶段继续的命令

### Step 4: Auto-approve Blueprint
**目标**: 自动批准 Blueprint（质量 > 85）
**操作**: 检查 Blueprint 质量分数
**输出**: 批准状态
**错误处理**: 质量低于 85 分时暂停供手动审查并提供改进建议；质量极低（<70分）时建议使用 /ccc:iterate 重新设计

### Step 5: Run /ccc:build
**目标**: 构建 Delivery 制品
**操作**: 从 Blueprint 生成交付物
**输出**: Delivery 制品（DLV-xxx）
**错误处理**: 构建失败时显示错误和 Blueprint ID 供手动构建；文件写入权限被拒时建议检查目录权限或指定其他输出目录

### Step 6: Show Final Summary
**目标**: 展示最终汇总
**操作**: 显示全流程结果
**输出**: 汇总报告
**错误处理**: 任一阶段失败时显示部分完成报告并标记失败阶段；生成的制品 ID 无效时列出可用制品供验证

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

## Examples

### Example 1: 快速创建简单的搜索工具

```bash
/ccc:quick "我想创建一个 Skill 来快速查找项目中的 TODO 注释"
```

**场景**: 从需求到交付的一键完成

**执行过程**:
```
┌─────────────────────────────────────────────────────┐
│ 📋 Stage 1: Intent Creation ✓ COMPLETED            │
├─────────────────────────────────────────────────────┤
│ ID: INT-2026-03-07-001                              │
│ Quality: 89/100  [█████████████████░░] 优秀         │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│ 📐 Stage 2: Blueprint Design ✓ COMPLETED           │
├─────────────────────────────────────────────────────┤
│ ID: BLP-2026-03-07-001                              │
│ Quality: 92/100  [██████████████████░] 优秀         │
│ Status: ✓ Auto-approved (质量 > 85)                 │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│ 📦 Stage 3: Delivery ✓ COMPLETED                   │
├─────────────────────────────────────────────────────┤
│ ID: DLV-2026-03-07-001                              │
│ Compliance: 88/100                                  │
│ Files: SKILL.md, README.md, tests/                  │
└─────────────────────────────────────────────────────┘

🚀 Quick Workflow Complete!
Total time: 3m 45s
Status: ✅ Ready to use
```

**生成文件**:
- `docs/ccc/intent/2026-03-07-INT-001.yaml`
- `docs/ccc/blueprint/2026-03-07-BLP-001.yaml`
- `docs/ccc/delivery/2026-03-07-DLV-001/SKILL.md`

### Example 2: 创建复杂工具（部分阶段需要人工审查）

```bash
/ccc:quick "我要做一个自动部署工具，支持 Kubernetes 和 Docker，需要回滚功能"
```

**场景**: 复杂需求，Blueprint 质量未达到自动批准阈值

**执行过程**:
```
┌─────────────────────────────────────────────────────┐
│ 📋 Stage 1: Intent Creation ✓ COMPLETED            │
│ Quality: 78/100                                     │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│ 📐 Stage 2: Blueprint Design ✓ COMPLETED           │
│ Quality: 82/100  [████████████████░░░] 良好         │
│ Status: ⚠ Manual review required (质量 < 85)        │
└─────────────────────────────────────────────────────┘

⚠ Blueprint quality below auto-approval threshold (82/100)

Suggestions:
1. Review workflow complexity (8 steps detected)
2. Consider adding more error handling
3. Validate tool selection rationale

Options:
- Press Enter to continue anyway
- Type 'stop' to pause and iterate
- Run /ccc:iterate --artifact-id=BLP-002 to improve

> [User presses Enter]

┌─────────────────────────────────────────────────────┐
│ 📦 Stage 3: Delivery ✓ COMPLETED                   │
└─────────────────────────────────────────────────────┘

⚠ Completed with warnings - Review recommended
```

### Example 3: 多语言支持（英文）

```bash
/ccc:quick "I want to create a log analyzer that parses nginx logs" --lang=en-us
```

**输出**:
```
🚀 Quick Workflow Complete!

┌─────────────────────────────────────────────────────┐
│ Full Pipeline Summary                               │
├─────────────────────────────────────────────────────┤
│ Intent    →  Blueprint   →  Delivery               │
│ 91/100 ✓     94/100 ✓      90/100 ✓                │
│                                                     │
│ Total time: 4m 12s                                  │
│ Status: ✅ All stages passed                        │
└─────────────────────────────────────────────────────┘

Next steps:
   1. 📖 Review the generated SKILL.md
   2. 🧪 Test with sample nginx logs
   3. 🔄 Iterate if needed with /ccc:iterate
```

### Example 4: 处理 Intent 质量过低的情况

```bash
/ccc:quick "做个工具"
```

**场景**: 需求描述过于模糊

**输出**:
```
┌─────────────────────────────────────────────────────┐
│ 📋 Stage 1: Intent Creation ✓ COMPLETED            │
│ Quality: 48/100  [█████░░░░░░░░░░░░░░░] 差          │
└─────────────────────────────────────────────────────┘

❌ Intent quality too low (48/100 < 60)

Issues detected:
- Requirement too vague
- Missing constraints
- Unclear objectives

⛔ Workflow stopped. Please provide more details:
1. What problem does it solve?
2. What are the inputs and outputs?
3. Any technical constraints?

Try again with: /ccc:quick "更详细的描述"
```

### Example 5: 处理构建失败并保留中间制品

```bash
/ccc:quick "创建一个数据迁移工具，支持 MySQL 和 PostgreSQL"
```

**场景**: 前两个阶段成功，构建阶段失败

**输出**:
```
┌─────────────────────────────────────────────────────┐
│ 📋 Stage 1: Intent ✓ | 📐 Stage 2: Blueprint ✓    │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│ 📦 Stage 3: Delivery ✗ FAILED                      │
└─────────────────────────────────────────────────────┘

❌ Build failed: Template rendering error

Partial completion:
  ✓ Intent created: INT-2026-03-07-005
  ✓ Blueprint created: BLP-2026-03-07-005
  ✗ Delivery failed at stage 3

Recovery options:
  1. Review Blueprint: cat docs/ccc/blueprint/2026-03-07-BLP-005.yaml
  2. Retry build: /ccc:build --artifact-id=BLP-005
  3. Iterate design: /ccc:iterate --artifact-id=BLP-005
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
