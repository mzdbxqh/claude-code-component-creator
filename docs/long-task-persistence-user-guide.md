# CCC 长任务持久化机制用户指南

**版本**: v3.2.0
**状态**: Production Ready
**最后更新**: 2026-03-16

---

## 目录

1. [概述](#概述)
2. [什么是长任务](#什么是长任务)
3. [为什么需要持久化](#为什么需要持久化)
4. [核心概念](#核心概念)
5. [快速开始](#快速开始)
6. [使用场景](#使用场景)
7. [常见问题](#常见问题)
8. [最佳实践](#最佳实践)

---

## 概述

CCC 长任务持久化机制提供了完整的断点恢复和中间结果保存能力，确保长时间运行的任务可以从任意中断点恢复执行，避免重复工作和成本浪费。

**核心特性**:
- ✅ **断点恢复**: 从任意步骤恢复执行
- ✅ **中间结果持久化**: 所有关键数据保存到文件
- ✅ **标准化目录结构**: 统一的文件组织方式
- ✅ **自动化检测**: design-core 自动识别长任务

---

## 什么是长任务

满足以下条件的任务被视为"长任务"：

```
步骤数 ≥ 5 步
  AND
(
  调用 SubAgent (≥1次)
  OR
  生成中间文件
  OR
  预计执行时间 > 3分钟
)
```

**典型案例**:
- ✅ review-aggregator（11步，调用多个 SubAgent）
- ✅ design-new-core（5阶段设计流程）
- ✅ blueprint-core（完整设计流程）
- ❌ std-component-selection（1步决策，无 SubAgent 调用）

---

## 为什么需要持久化

### 问题场景

**场景1：长任务中断**
```
1. 用户执行 /cmd-review
2. Step 0-7 完成（约 45 分钟，成本 $1.20+）
3. Step 8 进行中...
4. 【中断】用户 Ctrl+C 或会话超时
5. 之前的工作全部丢失
6. 必须重新开始 ❌
```

**场景2：有了持久化**
```
1. 用户执行 /cmd-review
2. Step 0-7 完成（每步保存中间结果）
3. Step 8 进行中...
4. 【中断】
5. 重新启动，检测到未完成事务
6. 用户选择"从断点恢复"
7. 从 Step 8 继续执行 ✅
```

### 效益

| 维度 | 无持久化 | 有持久化 |
|------|---------|---------|
| 中断后恢复 | 必须重新开始 | 从断点继续 |
| 时间成本 | 30-60 分钟 | 数秒（加载） |
| 金钱成本 | $1.20-$2.40/次 | 可忽略 |
| 用户体验 | 挫败感强 | 无缝恢复 |

---

## 核心概念

### 事务 (Transaction)

一次完整的长任务执行，具有唯一的事务 ID。

**事务 ID 格式**: `{workflow-type}-{YYYYMMDD}-{HHMMSS}`

**示例**:
- `review-20260316-143022`
- `design-20260316-150130`

### Checkpoint

保存事务状态和元数据的 JSON 文件。

**位置**: `.checkpoints/{transaction-id}.json`

**关键字段**:
- `transaction_id`: 事务唯一标识
- `status`: 事务状态（in_progress / completed / failed）
- `current_step`: 当前执行步骤
- `key_files`: 关键文件路径映射
- `statistics`: 统计信息

### 数据目录

存储中间结果和最终报告的目录。

**位置**: `docs/{transaction-id}/{component-name}/`

**文件类型**:
- **配置文件**: `{key}.json`
- **中间结果**: `{key}-results.json`
- **最终报告**: `YYYY-MM-DD-{name}.md`
- **批量文件**: `{category}-results/`

---

## 快速开始

### 1. 查看持久化组件

以 review-aggregator 为例：

```bash
# 查看 SKILL.md
cat claude-code-component-creator/agents/reviewer/review-aggregator/SKILL.md
```

关键步骤：
- **Step 0.0**: 检查是否有未完成的事务
- **Step 0.1.1**: 初始化持久化事务
- **Step 0.4.1**: 保存组件列表
- **Step 2**: 保存验证结果
- **Step 9**: 完成事务

### 2. 执行长任务

```bash
# 启动任务（会自动初始化事务）
/cmd-review

# 如果中断，重新启动会询问是否恢复
```

### 3. 查看事务状态

```bash
# 列出所有未完成的事务
bash scripts/persistence/list-transactions.sh review in_progress

# 查看 checkpoint 内容
cat .checkpoints/review-20260316-143022.json | jq .

# 查看数据目录
ls -la docs/review-20260316-143022/review-aggregator/
```

### 4. 恢复执行

重新启动任务时，系统会自动检测未完成的事务并询问：

```
发现未完成的 review 事务，是否恢复？

选项:
1. 从断点恢复 - 继续之前中断的审查
2. 重新开始 - 忽略之前的进度，重新执行
```

选择"从断点恢复"即可继续。

---

## 使用场景

### 场景1：正常执行流程

```bash
# 1. 启动任务
/cmd-review

# 2. 系统自动：
#    - 初始化事务: review-20260316-143022
#    - 创建数据目录: docs/review-20260316-143022/review-aggregator/
#    - 创建 checkpoint: .checkpoints/review-20260316-143022.json

# 3. 执行过程中：
#    - Step 0.4.1: 保存组件列表
#    - Step 2: 保存验证结果
#    - Step 9: 标记事务完成

# 4. 完成后：
#    - 生成最终报告
#    - checkpoint.status = "completed"
```

### 场景2：中断恢复流程

```bash
# 1. 任务在 Step 5 中断
# 2. checkpoint 保存: current_step = 5

# 3. 重新启动
/cmd-review

# 4. 系统检测到未完成事务
#    "发现未完成的 review 事务，是否恢复？"

# 5. 用户选择"从断点恢复"

# 6. 系统：
#    - 加载 checkpoint
#    - 读取 current_step = 5
#    - 从文件加载之前保存的数据
#    - 跳转到 Step 6 继续执行

# 7. 完成执行
```

### 场景3：手动清理旧事务

```bash
# 清理 30 天前的已完成事务
bash scripts/persistence/cleanup-old-transactions.sh 30

# 输出:
# Cleaning up transactions older than 30 days...
# Deleting: docs/review-20260216-143022 (status: completed)
# Deleting: .checkpoints/review-20260216-143022.json (status: completed)
# Cleanup complete:
#   - Deleted 1 data directories
#   - Deleted 1 checkpoint files
```

---

## 常见问题

### Q1: 如何判断一个任务是否支持持久化？

**A**: 查看组件的 SKILL.md，搜索 `scripts/persistence/` 关键字。如果包含持久化脚本调用，说明支持持久化。

已支持的组件：
- ✅ review-aggregator
- ✅ 未来: design-new-core, blueprint-core（计划中）

### Q2: 中断后必须从断点恢复吗？

**A**: 不是。系统会询问你选择：
- **从断点恢复**: 继续之前的工作
- **重新开始**: 忽略之前的进度，创建新事务

### Q3: 数据保存在哪里？

**A**: 两个位置：
1. **数据目录**: `docs/{transaction-id}/{component-name}/`（中间结果和最终报告）
2. **Checkpoint**: `.checkpoints/{transaction-id}.json`（元数据）

### Q4: 如何清理旧的事务数据？

**A**: 使用清理脚本：

```bash
# 清理 30 天前的已完成事务
bash scripts/persistence/cleanup-old-transactions.sh 30
```

### Q5: 性能开销是多少？

**A**: 非常低（<0.02%）：
- 初始化事务: ~50ms
- 保存文件: ~30ms
- 更新 checkpoint: ~20ms
- 完成事务: ~60ms

对于 30-60 分钟的长任务，总开销 ~180ms，可忽略。

### Q6: 是否支持并行执行？

**A**: 支持，每个事务有独立的事务 ID 和数据目录，互不干扰。

### Q7: checkpoint 文件会提交到 Git 吗？

**A**: 不会。`.gitignore` 已配置忽略：
- `.checkpoints/`（checkpoint 文件）
- `docs/*/*/`（中间文件）
- 保留 `docs/*/*/*.md`（最终报告）

---

## 最佳实践

### 1. 定期清理旧事务

```bash
# 每月清理 30 天前的已完成事务
bash scripts/persistence/cleanup-old-transactions.sh 30
```

### 2. 验证 checkpoint 完整性

```bash
# 运行验证脚本
bash scripts/persistence/validate-checkpoint.sh .checkpoints/review-xxx.json
```

### 3. 备份重要的中间结果

如果某个中间结果特别重要，可以手动备份：

```bash
cp docs/review-xxx/review-aggregator/key-file.json backups/
```

### 4. 使用描述性的统计信息

在更新 checkpoint 时，提供清晰的统计信息：

```bash
bash scripts/persistence/update-checkpoint.sh $TRANSACTION_ID 5 \
  '{"reviews_completed":16,"reviews_failed":0,"total_issues":45}'
```

### 5. 错误处理

如果任务失败，使用 `failed` 状态完成事务：

```bash
bash scripts/persistence/finalize-transaction.sh $TRANSACTION_ID failed
```

---

## 参考文档

- [持久化迁移指南](persistence-migration-guide.md)
- [脚本使用文档](../scripts/persistence/README.md)
- [设计规范](../../docs/2026-03-16-long-task-persistence-standard-design.md)
- [反模式规则](../agents/reviewer/knowledge/antipatterns/persistence/)

---

**版本历史**:
- v3.2.0 (2026-03-16): 首次发布
