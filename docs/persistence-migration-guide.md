# CCC 长任务持久化迁移指南

**版本**: v3.2.0
**目标读者**: CCC 组件开发者
**前置条件**: 了解 SKILL.md 语法和 Workflow 设计
**最后更新**: 2026-03-16

---

## 目录

1. [迁移概述](#迁移概述)
2. [迁移前准备](#迁移前准备)
3. [迁移步骤](#迁移步骤)
4. [迁移验证](#迁移验证)
5. [常见问题](#常见问题)
6. [迁移案例](#迁移案例)

---

## 迁移概述

本指南帮助你将现有的长任务组件迁移到持久化架构，实现断点恢复和中间结果保存。

### 迁移目标

将这样的流程：
```
Step 0 → [内存] → Step 1 → [内存] → ... → Step 9 → [文件]
```

迁移到：
```
Step 0 → [文件] → Step 1 → [文件] → ... → Step 9 → [文件]
         ↓               ↓                      ↓
      checkpoint      checkpoint          checkpoint
```

### 迁移范围

**适用组件**:
- ✅ 步骤数 ≥ 5
- ✅ 调用 SubAgent (≥1次)
- ✅ 生成中间文件
- ✅ 预计执行时间 > 3分钟

**不适用组件**:
- ❌ 简单决策类组件（如 std-component-selection）
- ❌ 纯知识库组件（如 lib-antipatterns）

---

## 迁移前准备

### 1. 备份当前版本

```bash
# 1.1 备份 SKILL.md
cp agents/xxx/SKILL.md agents/xxx/SKILL.md.backup-pre-persistence

# 1.2 创建 Git tag
git tag -a v3.1.0-pre-persistence -m "Backup before persistence migration"
git push origin v3.1.0-pre-persistence
```

### 2. 分析当前工作流

创建分析文档 `docs/{component-name}-persistence-migration-baseline.md`：

```markdown
# {Component Name} 持久化迁移基线分析

## 当前功能

[描述当前组件功能]

## 工作流步骤

- Step 0: [描述]
- Step 1: [描述]
- ...

## 数据流分析

| 步骤 | 输入数据 | 输出数据 | 当前传递方式 | 迁移后 |
|------|---------|---------|-------------|--------|
| Step 0 | 无 | 组件列表 | 内存 | 文件 |
| Step 1 | 组件列表 | 审查结果 | 内存 | 文件 |
| ... | ... | ... | ... | ... |

## 关键步骤识别

[标识需要保存中间结果的关键步骤]

## 迁移目标

[定义迁移完成的标准]
```

### 3. 识别关键步骤

关键步骤的特征：
- ✅ 生成重要的中间结果
- ✅ 调用耗时的 SubAgent
- ✅ 执行复杂计算
- ✅ 后续步骤依赖其输出

---

## 迁移步骤

### Step 1: 添加事务恢复检查（Step 0.0）

在 Workflow 最开始添加：

```markdown
### Step 0.0: 检查是否有未完成的事务

**操作**: 检测和恢复未完成的事务

```bash
pending_transactions=$(bash scripts/persistence/list-transactions.sh {workflow-type} in_progress)

if [[ -n "$pending_transactions" ]]; then
    response = AskUserQuestion({
      "questions": [{
        "question": "发现未完成的 {workflow-type} 事务，是否恢复？",
        "header": "恢复选项",
        "multiSelect": false,
        "options": [
          {
            "label": "从断点恢复",
            "description": "继续之前中断的执行"
          },
          {
            "label": "重新开始",
            "description": "忽略之前的进度，重新执行"
          }
        ]
      }]
    })

    if response == "从断点恢复":
        # 加载 checkpoint
        TRANSACTION_ID = extract_transaction_id(pending_transactions)
        checkpoint = Read(.checkpoints/${TRANSACTION_ID}.json)
        resume_from_step = checkpoint.current_step + 1

        # 跳转到断点
        goto Step {resume_from_step}
    else:
        # 重新开始
        TRANSACTION_ID = "{workflow-type}-$(date +%Y%m%d-%H%M%S)"
fi
```
```

### Step 2: 添加事务初始化（Step 0.1）

在原 Step 0 之后添加：

```markdown
### Step 0.1: 初始化持久化事务

**操作**: 创建事务和数据目录

```bash
# 如果不是恢复模式，初始化新事务
if [[ -z "$TRANSACTION_ID" ]]; then
    TRANSACTION_ID="{workflow-type}-$(date +%Y%m%d-%H%M%S)"

    result=$(bash scripts/persistence/init-transaction.sh {workflow-type} $TRANSACTION_ID {component-name})

    # 验证初始化成功
    if [[ $(echo "$result" | jq -r '.status') != "success" ]]; then
        echo "Error: Transaction initialization failed"
        exit 1
    fi
fi
```
```

### Step 3: 在关键步骤后添加保存操作

**模式A: 单个文件保存**

```markdown
### Step N: [原有步骤名称]

**操作**: [原有操作]

```bash
# [原有步骤代码]

# === 持久化：保存步骤结果 ===
Write(file_path="/tmp/step-{n}-results.json", content=json(results))

bash scripts/persistence/save-file.sh \
  $TRANSACTION_ID \
  step_{n}_results \
  intermediate-result \
  /tmp/step-{n}-results.json

# 更新 checkpoint
bash scripts/persistence/update-checkpoint.sh \
  $TRANSACTION_ID \
  {n} \
  '{"step_name":"...", "records_processed": N}'
```
```

**模式B: 批量文件保存（SubAgent 循环）**

```markdown
### Step N: [原有步骤名称]

**操作**: [原有操作]

```bash
FOR item IN items DO
    result = Agent(subagent-name, item)

    # === 持久化：保存每个结果 ===
    Write(file_path="/tmp/result-${item}.json", content=result)

    bash scripts/persistence/save-file.sh \
      $TRANSACTION_ID \
      $item \
      intermediate-result \
      /tmp/result-${item}.json \
      results-dir  # 子目录
END FOR

# 更新 checkpoint
bash scripts/persistence/update-checkpoint.sh \
  $TRANSACTION_ID \
  {n} \
  '{"completed": '${len(items)}'}'
```
```

### Step 4: 修改数据加载逻辑

将内存传递改为文件加载：

**迁移前**:
```bash
# Step 1: 生成数据
data = compute_data()

# Step 2: 使用数据
process(data)  # 从内存读取
```

**迁移后**:
```bash
# Step 1: 生成并保存数据
data = compute_data()
Write(file_path="/tmp/data.json", content=json(data))
bash scripts/persistence/save-file.sh $TRANSACTION_ID data config /tmp/data.json

# Step 2: 从文件加载数据
data_content=$(bash scripts/persistence/load-file.sh $TRANSACTION_ID data)
data = json.loads(data_content)
process(data)  # 从文件读取
```

### Step 5: 添加事务完成标记（最后一步）

在最后一步添加：

```markdown
### Step Final: [原有最后步骤名称]

**操作**: [原有操作]

```bash
# [原有步骤代码]

# === 持久化：完成事务 ===
bash scripts/persistence/finalize-transaction.sh $TRANSACTION_ID completed

# 验证完成
if [[ $? -eq 0 ]]; then
    echo "✅ Transaction completed successfully"
else
    echo "❌ Transaction finalization failed"
fi
```
```

---

## 迁移验证

### 1. 单元测试

运行持久化脚本的单元测试：

```bash
bash scripts/persistence/tests/test-init-transaction.sh
bash scripts/persistence/tests/test-save-load.sh
bash scripts/persistence/tests/test-checkpoint-update.sh
bash scripts/persistence/tests/test-validation.sh
```

### 2. 集成测试：正常执行

```bash
# 清理旧数据
rm -rf docs/{workflow-type}-* .checkpoints/{workflow-type}-*

# 执行完整流程
/cmd-{component-name}

# 验证 checkpoint
ls -la .checkpoints/{workflow-type}-*.json

# 验证数据目录
ls -la docs/{workflow-type}-*/{component-name}/

# 验证最终报告
cat docs/{workflow-type}-*/{component-name}/*.md
```

### 3. 集成测试：中断恢复

```bash
# 1. 启动任务，在中间步骤人工停止（Ctrl+C）

# 2. 验证 checkpoint 保存
cat .checkpoints/{workflow-type}-*.json | jq .

# 3. 重新启动
/cmd-{component-name}

# 4. 选择"从断点恢复"

# 5. 验证恢复正确（从断点继续，不重复执行）

# 6. 完成执行

# 7. 验证最终结果正确
```

### 4. 性能测试

```bash
# 测试性能开销
time /cmd-{component-name}  # 迁移后
# 对比之前的基线时间

# 预期：性能开销 < 10%
```

---

## 常见问题

### Q1: 如何处理已经执行到一半的步骤？

**A**: 如果步骤未完成，从该步骤重新开始：

```markdown
### Step N: [步骤名称]

**操作**:

```bash
# 检查是否已完成（通过 checkpoint）
completed=$(jq -r '.statistics.step_N_completed' .checkpoints/${TRANSACTION_ID}.json)

if [[ "$completed" == "true" ]]; then
    echo "Step N already completed, skipping"
    goto Step N+1
fi

# 执行步骤
[正常执行代码]

# 标记完成
bash scripts/persistence/update-checkpoint.sh $TRANSACTION_ID N '{"step_N_completed":true}'
```
```

### Q2: 如何处理失败的任务？

**A**: 使用 `failed` 状态完成事务：

```markdown
### Step N: [步骤名称]

**操作**:

```bash
# Try执行
if ! execute_step; then
    # 失败处理
    bash scripts/persistence/finalize-transaction.sh $TRANSACTION_ID failed
    echo "❌ Task failed at Step N"
    exit 1
fi
```
```

### Q3: 迁移后性能变差怎么办？

**A**: 优化保存策略：
1. 只保存关键步骤的结果
2. 使用更快的存储（SSD）
3. 压缩大文件

### Q4: 如何处理多个组件的迁移？

**A**: 按优先级逐个迁移：
1. P0: review-aggregator（已完成）
2. P1: design-new-core, blueprint-core
3. P2: 其他组件

---

## 迁移案例

### 案例1: review-aggregator

**迁移前**:
- 11个步骤，全部在内存中传递数据
- 中断后必须重新开始
- 无checkpoint机制

**迁移后**:
- 添加 Step 0.0（恢复检查）和 Step 0.1.1（事务初始化）
- 在 Step 0.4.1、Step 2、Step 9 保存关键数据
- 支持从任意步骤恢复
- checkpoint 完整记录状态

**性能影响**:
- 开销: ~220ms
- 原执行时间: 30-60 分钟
- 性能增加: <0.02%

**文件变更**:
- 修改: `agents/reviewer/review-aggregator/SKILL.md`（586行新增，37行删除）
- 提交: `0a3d5bb`

**验证**:
- ✅ 40个单元测试通过
- ✅ 5个集成点验证通过
- ✅ 性能影响可忽略

---

## 参考文档

- [用户指南](long-task-persistence-user-guide.md)
- [脚本使用文档](../scripts/persistence/README.md)
- [设计规范](../../docs/2026-03-16-long-task-persistence-standard-design.md)
- [review-aggregator 迁移基线](../../docs/review-aggregator-persistence-migration-baseline.md)
- [review-aggregator 迁移完成报告](../../docs/review-aggregator-persistence-migration-complete.md)

---

**版本历史**:
- v3.2.0 (2026-03-16): 首次发布
