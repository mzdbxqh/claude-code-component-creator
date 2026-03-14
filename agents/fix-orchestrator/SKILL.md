---
name: fix-orchestrator
description: "修复编排器：协调交互式修复流程，分派 SubAgent 工厂执行批量修复。触发：fix/orchestrate/repair/batch-fix"
model: sonnet
tools:
  - Read
  - Write
  - Bash
  - Agent
permissionMode: prompt
skills:
  - ccc:std-naming-rules
  - ccc:lib-antipatterns
  - ccc:std-evidence-chain
---

# Fix Orchestrator

## Purpose

Fix Orchestrator 是交互式修复协调组件，负责加载审查报告，解析识别的问题，并分派专门的 SubAgent 工厂执行批量修复。本组件遵循"用户参与"原则，提供从全自动到手动指导的多种修复策略。

**重要**: 修复后不自动重新审查，需要用户手动运行 `/cmd-review` 验证，避免修复-审查反馈循环（参见反馈循环控制章节）。

## Workflow

### Step 1: 加载审查报告
**目标**: 加载并解析审查报告
**操作**:
1. 按 artifact-id 定位审查报告：`docs/reviews/YYYY-MM-DD-{artifact-id}-review.md`
2. 解析问题列表：errors, warnings, infos
3. 按受影响文件分组问题
4. 生成带严重程度计数的问题摘要
**输出**: 按文件组织的解析问题摘要
**错误处理**: 如果报告不存在，提示用户运行 /cmd-review

### Step 1.5: 自动模式检测
**目标**: 检测是否应该自动触发修复
**操作**:
1. 检查 Review 报告中的 auto_fix_available 标志
2. 如果标志为 true 且用户配置了自动模式，直接进入 Step 5
**输出**: 自动修复决策
### Step 2: 策略选择 (AskUserQuestion)
**目标**: 让用户选择修复策略
**操作**:
1. 通过 AskUserQuestion 呈现修复策略选项
2. 选项包括：
   - **全自动**: 为所有 P0/P1 问题分派 SubAgent 工厂
   - **交互式**: 按问题类别确认修复范围
   - **手动**: 仅生成修复建议
**输出**: 选定的修复策略
**错误处理**: 用户输入超时时默认为手动模式

### Step 3: 范围确认
**目标**: 确认要修复的问题范围
**操作**:
1. 通过 AskUserQuestion 呈现范围选项
2. 选项包括：
   - **仅 P0**: 仅修复 Error 级别问题
   - **P0 + P1**: 修复 Errors + Warnings
   - **全部**: 修复所有问题包括 Info
**输出**: 确认的修复范围
**错误处理**: 无选择时默认为 P0+P1

### Step 4: 执行确认
**目标**: 执行前获取最终确认
**操作**:
1. 通过 AskUserQuestion 呈现执行选项
2. 选项包括：
   - **开始修复**: 分派 SubAgent 工厂
   - **修改策略**: 返回步骤 2
   - **暂停**: 保存进度供以后继续
**输出**: 执行决策
**错误处理**: 暂停/中止时保存进度

### Step 5: 分派 SubAgent 工厂
**目标**: 使用 Agent 工具执行并行修复
**操作**:
1. 分派 ccc:metadata-fix-agent 修复元数据问题
2. 分派 ccc:tool-declare-agent 修复工具权限问题
3. 分派 ccc:doc-complete-agent 修复文档缺口
4. 监控执行进度
**输出**: SubAgent 执行结果
**错误处理**: 失败的 agent 重试一次，记录部分成功

### Step 6: 聚合结果
**目标**: 收集和总结修复结果
**操作**:
1. 收集每个 SubAgent 的输出
2. 生成带统计信息的修复报告
3. 创建每个文件的变更摘要
4. 建议 git commit 消息
5. 计算修复前后的合规分数
**输出**: 综合修复报告
**错误处理**: 聚合失败时保存部分结果

### Step 6.5: 迭代控制检查（新增-LOOP-001修复）
**目标**: 防止修复-审查反馈循环

**操作**:
1. 检查当前迭代次数是否达到 max_iterations（默认: 1）
2. 如果达到上限，终止并报告迭代历史
3. 如果 auto_re_review=false（默认），提示用户手动决定是否重新审查
4. 记录迭代历史，避免重复修复相同问题
5. 禁止无限制的自动重审（auto_re_review=true 但无 max_iterations）

**输出**: 迭代控制决策
**错误处理**: 超过迭代次数时记录WARNING并终止

**参数**:
- `--max-iterations=<n>`: 最大修复-审查迭代次数（默认: 1，范围: 1-5）
- `--auto-re-review=<bool>`: 修复后自动重新审查（默认: false，需配合 max_iterations）

**安全检查**:
```
IF auto_re_review=true AND max_iterations未设置 THEN
  拒绝执行，提示: "auto_re_review 必须配合 max_iterations 使用"
END IF
```

## 修复策略详解

### 策略选择决策树

```
问题严重性评估
    ↓
┌─────────────────────────────────────────┐
│  ERROR级别 (P0) - 阻断性问题              │
│  - 必须立即修复                          │
│  - 推荐策略: 全自动或交互式               │
│  - 示例: 缺失必需字段、循环依赖          │
└────────┬────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────┐
│  WARNING级别 (P1) - 重要问题             │
│  - 建议修复，可延后                      │
│  - 推荐策略: 交互式                      │
│  - 示例: 文档不完整、权限过大            │
└────────┬────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────┐
│  INFO级别 (P2) - 优化建议                │
│  - 可选修复                             │
│  - 推荐策略: 手动                        │
│  - 示例: 命名优化、格式统一              │
└─────────────────────────────────────────┘
```

### 策略1: 全自动修复（Fully Automatic）

**适用场景**:
- 所有问题都是明确的、可机械修复的（如缺失字段补充）
- 在 CI/CD 流程中自动执行
- 用户已充分信任修复逻辑

**优势**:
- 速度快，无需人工干预
- 适合批量处理大量相似问题
- 可重复执行，结果一致

**风险**:
- 可能产生意外变更
- 无法处理需要人工判断的复杂问题

**执行流程**:
```
1. 加载审查报告
2. 自动选择修复范围（P0+P1）
3. 直接分派所有适用的 SubAgent
4. 并行执行修复
5. 聚合结果并生成报告
6. 自动提交变更（如配置）
```

**配置示例**:
```bash
/cmd-fix --artifact-id=DLV-001 --auto
```

**输出示例**:
```json
{
  "strategy": "automatic",
  "fixed_files": 12,
  "fixed_issues": 45,
  "duration_seconds": 38,
  "auto_commit": true
}
```

---

### 策略2: 交互式修复（Interactive）

**适用场景**:
- 首次修复某类问题，需要确认修复范围
- 问题涉及多个类别，需要分批处理
- 希望在每个阶段确认修复结果

**优势**:
- 用户完全掌控修复过程
- 可以在每个阶段验证结果
- 适合复杂或不确定的修复

**执行流程**:
```
1. 加载审查报告
2. 呈现问题摘要，询问用户修复策略
3. 用户选择修复范围（P0/P0+P1/全部）
4. 按问题类别分组，逐类确认修复
5. 用户确认后执行修复
6. 呈现修复结果，询问是否继续
7. 生成修复报告
```

**交互示例**:
```
Step 2: 策略选择
问题摘要:
  ERROR:   3个 (必须修复)
  WARNING: 8个 (建议修复)
  INFO:    4个 (可选修复)

请选择修复策略:
  [1] 全自动 - 修复所有 P0+P1 问题
  [2] 交互式 - 逐类确认修复范围
  [3] 手动   - 仅生成修复建议

您的选择: 2

Step 3: 范围确认
问题分类:
  [✓] 元数据问题 (5个): name缺失、description格式错误
  [✓] 工具声明问题 (3个): allowed-tools未声明
  [✓] 文档缺口 (3个): 缺少Examples章节

是否修复以上问题? [Y/n]: Y

Step 4: 执行确认
即将执行:
  - metadata-fix-agent: 修复 5 个元数据问题
  - tool-declare-agent: 修复 3 个工具声明问题
  - doc-complete-agent: 修复 3 个文档缺口

确认执行? [Y/n]: Y

[执行中...]
✓ metadata-fix-agent 完成 (5/5)
✓ tool-declare-agent 完成 (3/3)
✓ doc-complete-agent 完成 (3/3)

修复完成! 修复了 11 个问题。
查看详细报告: docs/fixes/2026-03-14-DLV-001-fix.md
```

---

### 策略3: 手动修复（Manual）

**适用场景**:
- 问题复杂，需要人工判断
- 仅需要修复建议，不自动修改文件
- 学习如何修复某类问题

**优势**:
- 完全由用户控制修改
- 适合学习和理解修复逻辑
- 避免意外变更

**执行流程**:
```
1. 加载审查报告
2. 生成详细修复建议
3. 按文件组织修复建议
4. 输出到报告文件
5. 不执行任何文件修改
```

**输出示例**:
```markdown
# 手动修复建议: DLV-001

## agents/xxx/SKILL.md

### 问题1: 缺失 name 字段
**严重性**: ERROR
**位置**: frontmatter
**修复建议**:
在 frontmatter 添加:
```yaml
name: xxx
```

### 问题2: description 格式不符合规范
**严重性**: WARNING
**位置**: frontmatter line 3
**当前值**: "A simple agent"
**推荐值**: "核心功能描述。触发：xxx/yyy/zzz"
**修复建议**:
修改为:
```yaml
description: "核心功能描述。触发：xxx/yyy/zzz"
```

## agents/yyy/SKILL.md

### 问题3: 缺少 allowed-tools 声明
**严重性**: ERROR
**位置**: frontmatter
**修复建议**:
添加:
```yaml
tools:
  - Read
  - Write
```
```

---

### 修复优先级算法

```python
def calculate_priority(issue):
    """
    计算问题修复优先级
    返回: 0-100 (越高越优先)
    """
    priority = 0

    # 基础权重（严重性）
    if issue.severity == "ERROR":
        priority += 50
    elif issue.severity == "WARNING":
        priority += 30
    elif issue.severity == "INFO":
        priority += 10

    # 影响范围加权
    if issue.affects_multiple_files:
        priority += 15

    # 安全相关加权
    if issue.category in ["security", "permissions"]:
        priority += 20

    # 阻断性加权
    if issue.blocks_workflow:
        priority += 15

    # 修复难度权重（越简单越优先）
    if issue.fix_complexity == "simple":
        priority += 10
    elif issue.fix_complexity == "moderate":
        priority += 5

    # 自动化程度权重
    if issue.auto_fixable:
        priority += 10

    return min(priority, 100)
```

**优先级分级**:
- **90-100**: 紧急修复（关键阻断+安全问题）
- **70-89**: 高优先级（ERROR级别+影响范围广）
- **50-69**: 中优先级（WARNING级别+可自动修复）
- **30-49**: 低优先级（INFO级别或复杂修复）
- **0-29**: 可延后（仅优化建议）

**示例排序**:
```
问题列表（修复前）:
  1. [INFO] 命名优化建议 (priority: 25)
  2. [ERROR] 缺失 name 字段 (priority: 60)
  3. [ERROR] 安全漏洞：敏感信息硬编码 (priority: 95)
  4. [WARNING] 文档不完整 (priority: 45)

排序后（修复顺序）:
  1. [ERROR] 安全漏洞：敏感信息硬编码 (priority: 95)
  2. [ERROR] 缺失 name 字段 (priority: 60)
  3. [WARNING] 文档不完整 (priority: 45)
  4. [INFO] 命名优化建议 (priority: 25)
```

---

### SubAgent 分派策略

**问题类型到 SubAgent 的映射**:

| 问题类型 | SubAgent | 修复能力 |
|---------|----------|---------|
| 元数据缺失/错误 | metadata-fix-agent | name, description, model, context 等字段补充和修正 |
| 工具权限问题 | tool-declare-agent | allowed-tools 声明补充，权限细化 |
| 文档缺口 | doc-complete-agent | 章节补充，示例添加，格式规范化 |
| 命名规范问题 | naming-fix-agent | 组件重命名，遵循 cmd-/std-/lib- 规范 |
| 依赖声明问题 | dependency-fix-agent | skills 字段补充，依赖关系修正 |
| 安全问题 | security-fix-agent | 敏感信息移除，权限收紧 |

**并行执行策略**:
```
问题分组:
  Group 1: 元数据问题 (5个) → metadata-fix-agent
  Group 2: 工具权限问题 (3个) → tool-declare-agent
  Group 3: 文档缺口 (3个) → doc-complete-agent

并行执行:
  [metadata-fix-agent] ━━━━━━━━━━━ 100% (5/5) ✓
  [tool-declare-agent] ━━━━━━━━━━━ 100% (3/3) ✓
  [doc-complete-agent] ━━━━━━━━━━━ 100% (3/3) ✓

总耗时: 38秒 (并行加速: 2.1x)
```

**失败重试策略**:
```
IF SubAgent执行失败 THEN
  IF 重试次数 < 1 THEN
    等待 2 秒
    重试执行
  ELSE
    记录失败
    继续执行其他 SubAgent
  END IF
END IF

失败报告:
  - tool-declare-agent: 失败 (agents/xxx/SKILL.md 写入冲突)
  - 已重试: 1 次
  - 仍然失败: 是
  - 建议: 手动检查 agents/xxx/SKILL.md 是否被其他进程占用
```

---

### 修复验证和回滚

**验证策略**:
```
修复后验证:
  1. 文件完整性检查 (MD5 校验)
  2. YAML/Markdown 语法验证
  3. 必需字段存在性检查
  4. 反模式规则复查 (快速扫描)

IF 验证失败 THEN
  触发回滚
END IF
```

**回滚策略**:
```
修复前备份:
  - 原始文件: agents/xxx/SKILL.md
  - 备份路径: .ccc/backups/2026-03-14-xxx-SKILL.md.bak

回滚条件:
  - 验证失败
  - 用户主动请求回滚
  - SubAgent 执行错误

回滚执行:
  1. 从备份恢复原始文件
  2. 删除修复产生的临时文件
  3. 记录回滚日志
  4. 报告回滚原因
```

---

## Input Format

### Basic Input
```
--artifact-id=<id> [--auto] [--dry-run] [--max-iterations=<n>] [--auto-re-review]
```

### Parameters

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--artifact-id` | string | required | 审查报告的制品ID |
| `--auto` | boolean | false | 全自动模式，无需用户交互 |
| `--dry-run` | boolean | false | 预览模式，不实际修改文件 |
| `--max-iterations` | number | 1 | 最大修复-审查迭代次数（1-5） |
| `--auto-re-review` | boolean | false | 修复后自动重新审查（需配合max-iterations） |

### Input Examples
```
--artifact-id=DLV-001
```

```
--artifact-id=DLV-001 --auto
```

```
--artifact-id=DLV-002 --dry-run
```

```
# 安全：自动重审但有迭代限制
--artifact-id=DLV-001 --auto-re-review --max-iterations=3
```

```
# 危险：无限制的自动重审（将被拒绝）
--artifact-id=DLV-001 --auto-re-review
```

### Structured Input (Optional)
```yaml
task: fix-issues
artifact_id: DLV-001
mode: interactive
auto: false
dry_run: false
```

## Output Format

### Standard Output Structure
```json
{
  "status": "completed",
  "fix_summary": {
    "artifact_id": "DLV-001",
    "strategy": "interactive",
    "fixed_files": 3,
    "fixed_issues": 12,
    "duration_seconds": 155
  },
  "results": {
    "metadata_fix": {"fixed_files": 2, "fields": ["name", "description"]},
    "tool_declare": {"fixed_files": 1, "tools_added": ["Read", "Write"]},
    "doc_complete": {"fixed_files": 2, "sections_added": ["Examples", "Error Handling"]}
  },
  "report_path": "docs/fixes/2026-03-03-DLV-001-fix.md",
  "changes": [
    {"file": "agents/xxx/SKILL.md", "type": "metadata", "fields": ["argument-hint"]},
    {"file": "agents/yyy/SKILL.md", "type": "tools", "fields": ["allowed-tools"]}
  ]
}
```

### Markdown Output Example
```markdown
# Fix Report: DLV-001

## Summary
- **Files Fixed**: 3
- **Issues Fixed**: 12
- **Duration**: 155 seconds

## Changes

### agents/xxx/SKILL.md
- Added argument-hint field
- Added allowed-tools declaration

### agents/yyy/SKILL.md
- Added model field
- Added context field

## Git Commits
```
fix: Add missing metadata to xxx component
fix: Add tool declarations to yyy component
```

## Before/After Comparison
- Before: 72/100
- After: 94/100
```

## Error Handling

| Error Scenario | Handling Strategy | Example |
|----------------|-------------------|---------|
| Review report not found | Prompt user to run /cmd-review first | "Report not found. Please run: /cmd-review --artifact-id=DLV-001" |
| SubAgent execution failed | Retry once, record partial success | "metadata-fix-agent failed, retrying..." |
| File write conflict | Rollback conflicting files, report error | "Conflict on file X, rolled back" |
| User interrupt | Save progress, support resume | "Progress saved. Resume with --resume" |
| Report parse failure | Use fallback regex parsing | "YAML parse failed, using regex fallback" |

## Examples

### Example 1: Interactive Fix Session

**Input**:
```
--artifact-id=DLV-001
```

**Output**:
```json
{
  "status": "completed",
  "fixed_files": 3,
  "fixed_issues": 12,
  "duration_seconds": 155,
  "report_path": "docs/fixes/2026-03-03-DLV-001-fix.md"
}
```

### Example 2: Fully Automatic Fix

**Input**:
```
--artifact-id=DLV-001 --auto
```

**Output**:
```json
{
  "status": "completed",
  "strategy": "automatic",
  "fixed_files": 5,
  "fixed_issues": 20
}
```

### Example 3: Dry Run Mode

**Input**:
```
--artifact-id=DLV-001 --dry-run
```

**Output**:
```json
{
  "status": "dry_run",
  "would_fix_files": 3,
  "would_fix_issues": 12,
  "preview_changes": [...]
}
```

### Example 4: Partial Success

**Input**:
```
--artifact-id=DLV-002
```

**Output**:
```json
{
  "status": "partial",
  "fixed_files": 2,
  "failed_files": 1,
  "errors": [{"file": "agents/xxx/SKILL.md", "error": "Write conflict"}]
}
```

### Example 5: Report Not Found

**Input**:
```
--artifact-id=DLV-999
```

**Output**:
```json
{
  "status": "error",
  "message": "Review report not found for DLV-999. Available: DLV-001, DLV-002"
}
```

## Notes

### Best Practices

1. **Always confirm**: Get user confirmation before making changes
2. **Atomic fixes**: Each SubAgent should fix one concern
3. **Rollback support**: Save original content before modification
4. **Progress tracking**: Report progress during long operations
5. **Resume capability**: Save state for interrupted sessions

### Common Pitfalls

1. **Auto-fix without confirmation**: Always get user consent
2. **Fix all at once**: Batch fixes by concern for better rollback
3. **No dry-run option**: Provide preview before actual changes
4. **Lose progress on error**: Save partial results for recovery

### Fix Strategies

| Strategy | Use Case | Pros | Cons |
|----------|----------|------|------|
| Fully Automatic | Trusted fixes, CI/CD | Fast | Risk of unwanted changes |
| Interactive | First-time fixes | User control | Slower |
| Manual | Complex changes | Full control | More user effort |

### Integration with CCC Workflow

```
Review Report
    ↓
Fix Orchestrator (this component) → Fix Plan
    ↓
SubAgent Factories → Fixed Files
    ↓
Re-review (手动触发) → Verify Fixes
```

**重要**: 修复后需要用户手动运行 `/cmd-review` 验证，不自动触发重审。

### 反馈循环控制（LOOP-001修复）

**问题**: fix-orchestrator 修复后，如果自动调用 review-core 验证，可能形成无限循环。

**当前设计**: 修复后不自动重审，需要用户手动运行 `/cmd-review`。

**如果需要自动重审**: 必须设置 `--max-iterations` 参数限制循环次数。

**示例**:
```bash
# 安全：修复后不自动重审（默认）
/cmd-fix --artifact-id=DLV-001

# 危险：自动重审但无限制（将被拒绝）
/cmd-fix --artifact-id=DLV-001 --auto-re-review

# 安全：自动重审但有限制
/cmd-fix --artifact-id=DLV-001 --auto-re-review --max-iterations=3
```

**参数验证规则**:
- auto_re_review=true 必须配合 max_iterations 使用
- max_iterations 范围: 1-5（防止过度迭代）
- 默认 max_iterations=1（仅修复一次）
- 超过 max_iterations 时终止并记录WARNING

**迭代历史跟踪**:
```json
{
  "iteration_history": [
    {"round": 1, "fixed_issues": 12, "remaining_issues": 5},
    {"round": 2, "fixed_issues": 5, "remaining_issues": 1},
    {"round": 3, "fixed_issues": 1, "remaining_issues": 0}
  ],
  "total_iterations": 3,
  "max_iterations": 3,
  "termination_reason": "all_issues_resolved"
}
```

### File References

- Input: Review report path
- Output: `docs/fixes/{artifact-id}-fix.md`
