---
name: cmd-fix
model: sonnet
context: fork
disable-model-invocation: true
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, Task]
description: "交互式修复审查问题。触发：修复/整改/改进。支持自动/交互/手动三种模式。"
argument-hint: "[--artifact-id=<id>] [--auto] [--dry-run]"
---

# /ccc:fix

**适用流程**:
- **主工作流**: `design` → `review` → **fix** → `validate` → `build`
- **代码迭代**: `implement` → `review` → **fix**
- **制品迭代**: `iterate` → `review` → **fix** → `build`

Interactive repair workflow with AskUserQuestion strategy selection and SubAgent factory execution.

## 模型要求

- **推荐**: Claude Sonnet 4.5+ (高效能,最佳性价比)
- **可用**: Claude Opus 4.5+ (最高质量,复杂问题修复)
- **最小**: Claude Sonnet 4.5+ (最低要求)

### 功能需求
- 需要支持 Tool Use (Bash, Read, Write, Edit, Glob, Grep, Task)
- 需要支持多轮对话和交互式决策
- 需要处理审查报告和问题修复
- 建议上下文窗口 >= 200K tokens (处理完整审查报告和代码修复)

## SubAgents 协作

本工作流使用以下 SubAgents 进行任务分解和并行执行：

### 核心 Agents
- **ccc:fix-orchestrator**: 修复编排器，协调交互式修复流程，分派 SubAgent 工厂执行批量修复
- **ccc:review-fix-connector**: 审查-修复连接器，解析审查报告并转换为修复任务
- **ccc:metadata-fix-agent**: 元数据修复代理，专门修复 frontmatter 字段缺失问题
- **ccc:tool-declare-agent**: 工具声明代理，补充 allowed-tools 字段
- **ccc:doc-complete-agent**: 文档补全代理，扩展 description 和补充缺失章节

### 调度策略
- **串行执行**: cmd-fix → ccc:fix-orchestrator → review-fix-connector → 并行派发修复 agents
- **并行执行**:
  - 按问题类型并行派发专门的修复 agents
  - 每个文件的修复串行执行，避免冲突
- **错误处理**:
  - 单个文件修复失败时记录错误，继续修复其他文件
  - 关键修复失败时终止流程并生成修复报告

### Agent 输入输出
| Agent | 输入 | 输出 |
|-------|------|------|
| ccc:fix-orchestrator | 审查报告 + 修复策略 | 修复任务分解 |
| ccc:review-fix-connector | 审查报告 | 结构化问题清单 |
| ccc:metadata-fix-agent | 文件路径 + 缺失字段 | 修复后的 frontmatter |
| ccc:tool-declare-agent | 文件路径 + 使用的工具列表 | 补充的 allowed-tools |
| ccc:doc-complete-agent | 文件路径 + 缺失章节 | 补充的文档内容 |

### 调用示例（全自动模式）
```
用户: /ccc:fix --artifact-id=DLV-001 --auto
  ↓
cmd-fix 读取审查报告
  ↓
调用 fix-orchestrator (策略=全自动)
  ↓
调用 review-fix-connector (解析问题)
  ↓
并行派发修复 agents:
  - metadata-fix-agent (修复 2 个文件的元数据)
  - tool-declare-agent (补充 3 个文件的工具声明)
  - doc-complete-agent (扩展 5 个文件的文档)
  ↓
聚合修复结果
  ↓
cmd-fix 输出修复摘要和报告
```

### 调用示例（交互式模式）
```
用户: /ccc:fix --artifact-id=DLV-001
  ↓
cmd-fix 读取审查报告并显示问题摘要
  ↓
AskUserQuestion: 选择修复策略
  用户选择: "交互式修复"
  ↓
AskUserQuestion: 选择修复范围
  用户选择: "P0 + P1"
  ↓
AskUserQuestion: 确认执行
  用户确认
  ↓
调用 fix-orchestrator (策略=交互式, 范围=P0+P1)
  ↓
... (后续流程同全自动模式)
```

### SubAgent 工厂模式
fix-orchestrator 采用工厂模式派发专门的修复 agents：
```
问题类型 → 对应的修复 Agent
├─ SKILL-001 (frontmatter 缺失) → metadata-fix-agent
├─ SKILL-002 (tools 未声明) → tool-declare-agent
├─ SKILL-003 (description 过短) → doc-complete-agent
├─ SKILL-004 (缺少示例) → doc-complete-agent
└─ ... (更多问题类型)
```

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--artifact-id` | 指定要修复的 artifact ID | 当前上下文 |
| `--auto` | 自动修复所有 P0 问题 | false |
| `--dry-run` | 预览修复内容，不实际写入 | false |

## 交互流程

### 步骤 1: 加载审查报告

```bash
/ccc:fix --artifact-id=DLV-001
```

系统加载最近的审查报告：
```
加载审查报告：docs/reviews/2026-03-03-DLV-001-review.md

问题摘要:
  - Errors:   2 个 (P0 - 必须修复)
  - Warnings: 5 个 (P1 - 建议修复)
  - Infos:    5 个 (P2 - 可选优化)

影响文件:
  - command/deploy.md (3 个问题)
  - skills/reviewer/SKILL.md (2 个问题)
  - agents/builder/SKILL.md (2 个问题)
```

### 步骤 2: 策略选择 (AskUserQuestion)

**目标**: 让用户选择修复策略
**操作**: 使用 AskUserQuestion 展示策略选项
**输出**: 用户选择的修复策略
**错误处理**: 用户取消选择时保留审查报告并退出；无有效选项时默认使用"手动修复"模式

```yaml
AskUserQuestion(
  questions=[{
    question: "发现 12 个问题，请选择修复策略：",
    header: "修复策略",
    options: [
      {
        label: "全自动修复",
        description: "派遣 SubAgent 工厂批量修复所有 P0/P1 问题（推荐）"
      },
      {
        label: "交互式修复",
        description: "逐类问题确认修复方案和范围"
      },
      {
        label: "手动修复",
        description: "仅生成修复建议，不执行修复"
      }
    ],
    multiSelect: false
  }]
)
```

### 步骤 3: 范围确认 (如选择交互式)

```yaml
AskUserQuestion(
  questions=[{
    question: "请选择要修复的问题类型：",
    header: "修复范围",
    options: [
      {
        label: "仅 P0 错误",
        description: "修复 2 个 Error 级别问题（元数据缺失、工具权限未声明）"
      },
      {
        label: "P0 + P1",
        description: "修复 7 个问题（包含 description 过短、缺少示例）"
      },
      {
        label: "全部修复",
        description: "修复所有 12 个问题（包含 Info 级别优化）"
      }
    ],
    multiSelect: false
  }]
)
```

### 步骤 4: 执行确认

```yaml
AskUserQuestion(
  questions=[{
    question: "确认修复策略，开始执行？",
    header: "执行确认",
    options: [
      {label: "开始修复", description: "派遣 SubAgent 工厂执行批量修复"},
      {label: "修改策略", description: "返回上一步重新选择"},
      {label: "暂停", description: "暂不执行，保留审查报告"}
    ],
    multiSelect: false
  }]
)
```

### 步骤 5: 并行修复执行

使用 `Agent` 工具并行调用 SubAgent 工厂：

```yaml
# 调用 ccc:metadata-fix-agent
Agent(
  subagent_type: "general-purpose",
  prompt: "修复以下文件的元数据问题：
    - command/deploy.md: 添加 argument-hint
    - skills/reviewer/SKILL.md: 添加 model 声明"
)

# 调用 ccc:tool-declare-agent
Task(
  subagent_type: "general-purpose",
  prompt: "为以下文件添加工具权限声明：
    - skills/reviewer/SKILL.md: allowed-tools"
)

# 调用 ccc:doc-complete-agent
Task(
  subagent_type: "general-purpose",
  prompt: "为以下文件添加使用示例：
    - agents/builder/SKILL.md"
)
```

**注意**: 实际执行时使用 `Agent` 工具，参数格式为：
- `subagent_type`: 指定子代理类型（如 `general-purpose`）
- `prompt`: 详细的修复指令

或者使用专用 SubAgent（如已定义）:
```yaml
Agent(
  subagent_type: "metadata-fix-agent",
  arguments: {
    files: ["command/deploy.md", "skills/reviewer/SKILL.md"],
    fix_types: ["argument-hint", "model"],
    dry_run: false
  }
)
```

### 步骤 6: 修复报告

```
修复完成！

修复摘要:
  - 修复文件数：3 个
  - 修复问题数：12 个
  - 修复耗时：2 分 35 秒

变更详情:
  ✓ command/deploy.md
    - 添加 argument-hint 字段
    - 补充错误处理文档

  ✓ skills/reviewer/SKILL.md
    - 添加 model: sonnet 声明
    - 添加 allowed-tools 声明

  ✓ agents/builder/SKILL.md
    - 添加使用示例章节

Git Commits:
  - chore: fix metadata issues in deploy.md
  - chore: add tool declarations in reviewer skill
  - docs: add examples to builder skill

修复报告：docs/fixes/2026-03-03-DLV-001-fix.md
```

## 输出规范

### 修复报告文件

| 属性 | 值 |
|------|-----|
| **目录** | `docs/fixes/` |
| **文件名** | `YYYY-MM-DD-<artifact-id>-fix.md` |
| **格式** | Markdown |

### 报告结构

| 章节 | 内容 |
|------|------|
| 修复摘要 | 修复文件数、问题数、耗时 |
| 变更详情 | 每个文件的变更列表 |
| Git Commits | 生成的提交记录 |
| 修复前后对比 | 合规评分对比 |

## 错误处理

| 错误场景 | 处理方式 |
|----------|----------|
| 审查报告不存在 | 提示先执行 /ccc:review |
| 无可修复问题 | 报告"无需修复"，退出 |
| 文件写入失败 | 回滚已修改文件，报告错误 |
| SubAgent 执行失败 | 重试 1 次，失败后报告部分成功 |
| Git 提交失败 | 保留修改，提示用户手动提交 |

## 安全考虑

### 输入验证

**artifact-id 验证**:
```python
def validate_artifact_id(artifact_id):
    """验证 artifact-id 格式，防止路径遍历"""
    # 仅允许字母、数字、连字符
    if not re.match(r'^[A-Z]+-\d+$', artifact_id):
        raise ValueError(f"Invalid artifact-id format: {artifact_id}")

    # 禁止路径遍历字符
    if '..' in artifact_id or '/' in artifact_id:
        raise SecurityError("Path traversal detected in artifact-id")

    return artifact_id
```

**文件路径验证**:
```python
def validate_file_path(file_path, base_dir):
    """验证文件路径在允许的目录内"""
    # 获取绝对路径
    abs_path = os.path.abspath(file_path)
    abs_base = os.path.abspath(base_dir)

    # 检查路径是否在基础目录下
    if not abs_path.startswith(abs_base):
        raise SecurityError(f"File path outside base directory: {file_path}")

    return abs_path
```

### 命令执行安全

**禁止直接执行用户输入**:
```bash
# ❌ 危险：字符串拼接
bash -c "fix_command: $user_input"

# ✅ 安全：使用数组和参数化
declare -a cmd_args=("$@")
bash -c "${cmd_args[@]}"

# ✅ 更安全：完全避免用户输入执行
# 使用白名单模式，仅调用预定义的 SubAgent
```

**SubAgent 调用安全**:
```python
# 使用白名单验证 SubAgent 类型
ALLOWED_SUBAGENTS = {
    'metadata-fix-agent',
    'tool-declare-agent',
    'doc-complete-agent'
}

def call_subagent(subagent_type, **kwargs):
    """安全地调用 SubAgent"""
    if subagent_type not in ALLOWED_SUBAGENTS:
        raise SecurityError(f"Unknown subagent type: {subagent_type}")

    # 调用前验证参数
    validate_subagent_params(kwargs)

    # 使用 Agent 工具调用
    return Agent(subagent_type=subagent_type, **kwargs)
```

### 文件操作安全

**防止覆盖关键文件**:
```python
# 关键文件和目录保护列表
PROTECTED_PATHS = {
    '.git',
    '.env',
    'credentials.json',
    'secrets.yaml'
}

def is_protected_path(file_path):
    """检查是否为受保护的路径"""
    for protected in PROTECTED_PATHS:
        if protected in file_path:
            return True
    return False

def safe_write_file(file_path, content):
    """安全地写入文件"""
    # 检查路径安全性
    validate_file_path(file_path, base_dir=PROJECT_ROOT)

    # 检查是否为受保护路径
    if is_protected_path(file_path):
        raise SecurityError(f"Cannot modify protected path: {file_path}")

    # 备份原文件
    if os.path.exists(file_path):
        backup_path = f"{file_path}.backup"
        shutil.copy2(file_path, backup_path)

    # 写入文件
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        # 恢复备份
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
        raise
```

### 权限最小化

**工具权限说明**:
- `Bash`: 仅用于 git 操作，不执行用户输入
- `Read/Write/Edit`: 仅操作项目目录内文件
- `Glob/Grep`: 仅用于文件搜索，不执行代码
- `Task`: 仅调用白名单中的 SubAgent

**运行时检查**:
```yaml
# 在 SKILL.md frontmatter 中声明
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, Task]
permissionMode: prompt  # 关键操作需要用户确认
```

### 审计日志

**记录关键操作**:
```python
def audit_log(operation, details):
    """记录审计日志"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'operation': operation,
        'details': details,
        'user': os.getenv('USER'),
        'artifact_id': current_artifact_id
    }

    with open('docs/audit.log', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

# 使用示例
audit_log('file_modified', {'path': 'skills/xxx/SKILL.md', 'changes': 3})
audit_log('subagent_called', {'type': 'metadata-fix-agent', 'files': 2})
```

### 安全检查清单

修复执行前的安全检查：

- [ ] artifact-id 格式验证（字母数字连字符）
- [ ] 文件路径验证（禁止路径遍历）
- [ ] 受保护文件检查（.git, .env, credentials）
- [ ] SubAgent 类型白名单验证
- [ ] 工具权限验证（仅使用声明的工具）
- [ ] 文件备份（修改前备份原文件）
- [ ] 审计日志（记录所有修改操作）

### 安全最佳实践

1. **永不直接执行用户输入**: 使用白名单和参数化调用
2. **最小权限原则**: 仅使用必要的工具权限
3. **输入验证**: 所有外部输入都要验证
4. **路径验证**: 确保所有文件操作在项目目录内
5. **备份机制**: 修改前备份，失败时回滚
6. **审计日志**: 记录所有关键操作

## 示例

### 示例 1: 交互式修复

```bash
/ccc:fix --artifact-id=DLV-001
```

### 示例 2: 自动修复 P0 问题

```bash
/ccc:fix --artifact-id=DLV-001 --auto
```

### 示例 3: 预览修复内容

```bash
/ccc:fix --artifact-id=DLV-001 --dry-run
```

### 示例 4: 与审查命令连用

```bash
# 先审查
/ccc:review --artifact-id=DLV-001

# 后修复
/ccc:fix --artifact-id=DLV-001
```

## 下一步

修复完成后：
1. 查看修复报告：`cat docs/fixes/YYYY-MM-DD-<artifact-id>-fix.md`
2. 验证修复结果：`/ccc:review --artifact-id=DLV-002` (新生成的 delivery)
3. 提交变更：`git add . && git commit -m "fix: 修复审查问题"`
