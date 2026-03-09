---
name: workflow-engine
description: "工作流引擎：外部状态管理→处理状态转换 + 错误恢复 + 恢复能力。触发：工作流/状态/进度/阶段/workflow/engine"
argument-hint: "<action> [args...]"
context: main
model: haiku
allowed-tools:
  - Read
  - Write
  - Bash
---

# Workflow Engine

## Purpose

Workflow Engine 是 CCC 工作流的状态管理和协调组件，负责外部状态管理、处理状态转换、错误恢复和恢复能力。本组件确保工作流各阶段有序执行，支持中断后恢复和多项目并行管理。

## Workflow

### Step 1: 接收工作流动作
**目标**: 解析工作流控制命令
**操作**:
1. 读取 action 参数 (init/start/pause/resume/stop/status)
2. 读取可选参数 (project-id, stage, options)
3. 验证动作合法性
**输出**: 工作流动作参数
**错误处理**: 动作无效时提示可用动作列表

### Step 2: 状态初始化
**目标**: 初始化或加载工作流状态
**操作**:
1. 检查工作流状态文件是否存在
2. 不存在则创建新状态 (init)
3. 存在则加载现有状态 (resume)
**输出**: 工作流状态对象
**错误处理**: 状态文件损坏时提示修复或重建

### Step 3: 状态转换验证
**目标**: 验证状态转换合法性
**操作**:

| 当前状态 | 允许转换 | 禁止转换 |
|----------|----------|----------|
| INIT | → IN_PROGRESS | → COMPLETED |
| IN_PROGRESS | → PAUSED/COMPLETED/FAILED | → INIT |
| PAUSED | → IN_PROGRESS/STOPPED | → COMPLETED |
| COMPLETED | (终态) | 任何 |
| FAILED | → IN_PROGRESS (修复后) | → COMPLETED |

**输出**: 状态转换决策
**错误处理**: 非法转换时拒绝并说明原因

### Step 4: 执行状态转换
**目标**: 更新工作流状态
**操作**:
1. 验证前置条件满足
2. 执行状态转换逻辑
3. 记录状态转换日志
4. 更新状态文件
**输出**: 状态转换结果
**错误处理**: 转换失败时回滚并报告

### Step 5: 错误处理与恢复
**目标**: 处理执行错误并支持恢复
**操作**:
1. 检测执行错误
2. 记录错误上下文
3. 保存检查点状态
4. 提供恢复指令
**输出**: 错误报告和恢复建议
**错误处理**: 错误级别分类处理

### Step 6: 生成状态报告
**目标**: 输出工作流状态摘要
**操作**:
1. 读取当前状态
2. 计算进度百分比
3. 生成下一步建议
4. 显示状态报告
**输出**: 状态报告
**错误处理**: 报告生成失败时返回原始状态

## Input Format

### 基本输入
```
<action> [args...]
```

### 输入示例
```
init --project=my-project
```

```
start --stage=stage1
```

```
resume
```

```
status --project=my-project
```

### 结构化输入 (可选)
```yaml
workflow:
  action: "start"
  args:
    projectId: "my-project"
    stage: "stage2"
    options:
      force: false
```

## Output Format

### 标准输出结构
```json
{
  "action": "start",
  "status": "SUCCESS",
  "workflowState": {
    "projectId": "my-project",
    "currentState": "IN_PROGRESS",
    "currentStage": "stage2",
    "progress": 40,
    "lastUpdated": "2026-03-03T10:30:00Z"
  },
  "nextAction": "执行 stage2 任务"
}
```

### 状态报告示例
```markdown
# 工作流状态：my-project

## 当前状态
- **状态**: IN_PROGRESS
- **阶段**: stage2 (Blueprint)
- **进度**: 40%
- **最后更新**: 2026-03-03 10:30

## 阶段历史
| 阶段 | 状态 | 完成时间 |
|------|------|----------|
| stage1 (Intent) | COMPLETED | 2026-03-03 09:00 |
| stage2 (Blueprint) | IN_PROGRESS | - |
| stage3 (Delivery) | PENDING | - |

## 下一步建议
运行 `/ccc:design` 完成 Blueprint 阶段
```

## Error Handling

| 错误场景 | 处理策略 | 示例 |
|----------|----------|------|
| 无效动作 | 提示可用动作列表 | "无效动作，可用：init/start/pause/resume/stop/status" |
| 状态文件损坏 | 提示修复或重建 | "状态文件损坏，是否重建？" |
| 非法状态转换 | 拒绝并说明原因 | "不能从 INIT 直接到 COMPLETED" |
| 前置条件不满足 | 列出缺失条件 | "stage1 未完成，不能开始 stage2" |
| 执行中断 | 保存检查点供恢复 | "执行中断，检查点已保存，运行 resume 恢复" |
| 状态文件写入失败 | 重试 1 次，内存保存 | "写入失败，状态保存在内存中" |

## Examples

### Example 1: 初始化工作流

**输入**:
```
init --project=my-project
```

**输出**:
```json
{
  "action": "init",
  "status": "SUCCESS",
  "workflowState": {
    "projectId": "my-project",
    "currentState": "INIT",
    "currentStage": null,
    "progress": 0
  },
  "nextAction": "运行 /ccc:init 开始 Stage 1"
}
```

### Example 2: 开始阶段

**输入**:
```
start --stage=stage1
```

**输出**:
```json
{
  "action": "start",
  "status": "SUCCESS",
  "workflowState": {
    "currentState": "IN_PROGRESS",
    "currentStage": "stage1",
    "progress": 10
  }
}
```

### Example 3: 暂停工作流

**输入**:
```
pause
```

**输出**:
```json
{
  "action": "pause",
  "status": "SUCCESS",
  "workflowState": {
    "currentState": "PAUSED",
    "currentStage": "stage2",
    "progress": 40
  },
  "resumeInstruction": "运行 resume 继续执行"
}
```

### Example 4: 恢复工作流

**输入**:
```
resume
```

**输出**:
```json
{
  "action": "resume",
  "status": "SUCCESS",
  "workflowState": {
    "currentState": "IN_PROGRESS",
    "currentStage": "stage2",
    "progress": 40
  },
  "checkpointRestored": true
}
```

### Example 5: 查看状态

**输入**:
```
status --project=my-project
```

**输出**:
```
工作流状态：my-project

当前状态：IN_PROGRESS
当前阶段：stage2 (Blueprint)
进度：40%

阶段历史:
  ✓ stage1 (Intent) - COMPLETED
  → stage2 (Blueprint) - IN_PROGRESS
  ○ stage3 (Delivery) - PENDING

下一步建议：运行 /ccc:design 完成 Blueprint 阶段
```

## Notes

### Best Practices

1. **状态持久化**: 所有状态变更写入文件
2. **检查点保存**: 关键操作前保存检查点
3. **转换验证**: 严格验证状态转换合法性
4. **日志记录**: 记录所有状态变更历史
5. **恢复友好**: 支持从中断点恢复执行

### Common Pitfalls

1. ❌ **状态丢失**: 不保存状态导致进度丢失
2. ❌ **非法转换**: 允许不合法的状态转换
3. ❌ **缺少检查点**: 执行中断后无法恢复
4. ❌ **日志缺失**: 无法追踪状态变更历史
5. ❌ **恢复复杂**: 恢复流程过于复杂

### State Machine

```
INIT → IN_PROGRESS → COMPLETED
              ↓
          PAUSED → IN_PROGRESS
              ↓
           STOPPED
              ↓
          FAILED → IN_PROGRESS (修复后)
```

### Actions

| 动作 | 用途 | 参数 |
|------|------|------|
| init | 初始化新工作流 | --project |
| start | 开始阶段 | --stage |
| pause | 暂停工作流 | - |
| resume | 恢复工作流 | - |
| stop | 停止工作流 | - |
| status | 查看状态 | --project |

### Integration with CCC Workflow

```
用户请求
    ↓
Workflow Engine (本组件) → 状态管理
    ↓
CCC Commands (/ccc:init, /ccc:design, etc.)
    ↓
状态更新 → 工作流推进
```

### File References

- 状态文件：`docs/ccc/workflow/{project-id}-state.yaml`
- 日志文件：`docs/ccc/workflow/{project-id}-log.md`
- 检查点：`docs/ccc/workflow/{project-id}-checkpoint.yaml`
