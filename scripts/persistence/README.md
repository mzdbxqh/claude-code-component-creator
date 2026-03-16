# CCC 持久化脚本使用文档

**版本**: v3.2.0
**目标读者**: CCC 组件开发者、脚本用户
**依赖**: Bash ≥ 4.0, jq ≥ 1.5
**最后更新**: 2026-03-16

---

## 目录

1. [脚本清单](#脚本清单)
2. [核心脚本](#核心脚本)
3. [工具脚本](#工具脚本)
4. [测试脚本](#测试脚本)
5. [库函数](#库函数)
6. [使用示例](#使用示例)
7. [故障排查](#故障排查)

---

## 脚本清单

```
scripts/persistence/
├── init-transaction.sh          # 初始化事务
├── save-file.sh                 # 保存文件
├── load-file.sh                 # 加载文件
├── update-checkpoint.sh         # 更新 checkpoint
├── finalize-transaction.sh      # 完成事务
├── list-transactions.sh         # 列出所有事务
├── validate-checkpoint.sh       # 验证 checkpoint
├── cleanup-old-transactions.sh  # 清理旧事务
├── lib/
│   ├── common.sh                # 通用函数
│   └── naming-rules.sh          # 命名规范
└── tests/
    ├── test-init-transaction.sh # 测试脚本
    ├── test-save-load.sh
    ├── test-checkpoint-update.sh
    ├── test-validation.sh
    └── benchmark.sh             # 性能测试
```

---

## 核心脚本

### init-transaction.sh

**用途**: 初始化新事务，创建目录结构和初始 checkpoint

**用法**:
```bash
bash scripts/persistence/init-transaction.sh <workflow-type> <transaction-id> [component-name]
```

**参数**:
- `workflow-type`: 工作流类型（review/design/blueprint/fix）
- `transaction-id`: 事务唯一标识（建议格式：{workflow}-{YYYYMMDD}-{HHMMSS}）
- `component-name`: （可选）执行组件名，默认为 workflow-type

**输出**（JSON 格式）:
```json
{
  "status": "success",
  "transaction_id": "review-20260316-143022",
  "data_dir": "docs/review-20260316-143022/review-aggregator/",
  "checkpoint_file": ".checkpoints/review-20260316-143022.json"
}
```

**错误码**:
- `1`: 事务已存在
- `2`: 参数错误或权限问题

**示例**:
```bash
# 初始化 review 类型事务
TRANSACTION_ID="review-$(date +%Y%m%d-%H%M%S)"
bash scripts/persistence/init-transaction.sh review $TRANSACTION_ID review-aggregator

# 验证创建成功
ls -la .checkpoints/$TRANSACTION_ID.json
ls -la docs/$TRANSACTION_ID/review-aggregator/
```

---

### save-file.sh

**用途**: 保存文件到事务目录，自动更新 checkpoint

**用法**:
```bash
bash scripts/persistence/save-file.sh <transaction-id> <key> <file-type> <content-file> [subdir]
```

**参数**:
- `transaction-id`: 事务 ID
- `key`: 文件逻辑键名（如 components_list, validated_results）
- `file-type`: 文件类型（config/intermediate-result/final-report/temp）
- `content-file`: 内容文件路径（临时文件）
- `subdir`: （可选）子目录，用于批量文件（如 review-results/）

**文件命名规则**:
| file_type | 生成的文件名 |
|-----------|-------------|
| config | `{key}.json` |
| intermediate-result | `{key}-results.json` |
| final-report | `YYYY-MM-DD-{key}.md` |
| temp | `{key}.tmp.json` |

**输出**（JSON 格式）:
```json
{
  "status": "success",
  "file_path": "docs/review-20260316-143022/review-aggregator/components-list.json",
  "relative_path": "components-list.json"
}
```

**示例**:
```bash
# 保存配置文件
echo '{"components": ["cmd-review", "std-component-selection"]}' > /tmp/components.json
bash scripts/persistence/save-file.sh $TRANSACTION_ID components_list config /tmp/components.json

# 保存中间结果
echo '{"validated": true}' > /tmp/validated.json
bash scripts/persistence/save-file.sh $TRANSACTION_ID validated_results intermediate-result /tmp/validated.json

# 保存批量文件到子目录
bash scripts/persistence/save-file.sh $TRANSACTION_ID cmd-review intermediate-result /tmp/review-1.json review-results
```

---

### load-file.sh

**用途**: 从事务加载文件内容

**用法**:
```bash
bash scripts/persistence/load-file.sh <transaction-id> <key>
```

**参数**:
- `transaction-id`: 事务 ID
- `key`: 文件逻辑键名

**输出**: 直接输出文件内容到 stdout

**错误码**:
- `1`: key 不存在（列出可用的 key）
- `2`: 文件不存在

**示例**:
```bash
# 加载并解析 JSON
components=$(bash scripts/persistence/load-file.sh $TRANSACTION_ID components_list)
echo "$components" | jq -r '.components[]'

# 加载到变量
validated_results=$(bash scripts/persistence/load-file.sh $TRANSACTION_ID validated_results)

# 错误处理
if ! data=$(bash scripts/persistence/load-file.sh $TRANSACTION_ID some_key 2>&1); then
    echo "Failed to load: $data"
    exit 1
fi
```

---

### update-checkpoint.sh

**用途**: 更新 checkpoint 的步骤和统计信息

**用法**:
```bash
bash scripts/persistence/update-checkpoint.sh <transaction-id> <step> <stats-json>
```

**参数**:
- `transaction-id`: 事务 ID
- `step`: 当前步骤编号
- `stats-json`: 统计信息 JSON 字符串

**输出**（JSON 格式）:
```json
{
  "status": "success",
  "checkpoint_updated": true,
  "current_step": 5
}
```

**示例**:
```bash
# 更新步骤和统计
bash scripts/persistence/update-checkpoint.sh $TRANSACTION_ID 5 \
  '{"reviews_completed":16,"reviews_failed":0}'

# 增量更新统计
bash scripts/persistence/update-checkpoint.sh $TRANSACTION_ID 6 \
  '{"total_issues":45}'

# 验证更新
jq '{current_step, statistics, last_updated}' .checkpoints/$TRANSACTION_ID.json
```

---

### finalize-transaction.sh

**用途**: 标记事务完成，可选清理临时文件

**用法**:
```bash
bash scripts/persistence/finalize-transaction.sh <transaction-id> <status>
```

**参数**:
- `transaction-id`: 事务 ID
- `status`: 最终状态（completed/failed）

**执行操作**:
1. 更新 checkpoint.status
2. 添加 completed_at 字段
3. 删除临时文件（*.tmp.json）
4. 生成事务摘要（transaction-summary.json）
5. 更新全局注册表

**输出**（JSON 格式）:
```json
{
  "status": "success",
  "transaction_completed": true,
  "final_status": "completed",
  "summary_file": "docs/review-20260316-143022/review-aggregator/transaction-summary.json"
}
```

**示例**:
```bash
# 成功完成
bash scripts/persistence/finalize-transaction.sh $TRANSACTION_ID completed

# 失败标记
bash scripts/persistence/finalize-transaction.sh $TRANSACTION_ID failed

# 验证状态
jq '.status' .checkpoints/$TRANSACTION_ID.json
```

---

## 工具脚本

### list-transactions.sh

**用途**: 列出所有事务

**用法**:
```bash
bash scripts/persistence/list-transactions.sh [workflow-type] [status]
```

**参数**:
- `workflow-type`: （可选）过滤工作流类型
- `status`: （可选）过滤状态（in_progress/completed/failed）

**输出**: 每行一个事务（JSON 格式）

**示例**:
```bash
# 列出所有事务
bash scripts/persistence/list-transactions.sh

# 列出所有未完成的 review 事务
bash scripts/persistence/list-transactions.sh review in_progress

# 列出所有已完成的事务
bash scripts/persistence/list-transactions.sh "" completed

# 解析输出
bash scripts/persistence/list-transactions.sh | jq -r '.transaction_id'
```

---

### validate-checkpoint.sh

**用途**: 验证 checkpoint 文件完整性和文件存在性

**用法**:
```bash
bash scripts/persistence/validate-checkpoint.sh <checkpoint-file>
```

**参数**:
- `checkpoint-file`: checkpoint 文件路径

**验证项**:
1. JSON 格式合法性
2. 必需字段完整性
3. key_files 引用的文件是否存在
4. 目录结构是否符合规范

**输出**:
```
✅ Checkpoint validation passed
Transaction: review-20260316-143022
Status: in_progress
Step: 5
Files: 4
```

**示例**:
```bash
# 验证 checkpoint
bash scripts/persistence/validate-checkpoint.sh .checkpoints/review-xxx.json

# 自动化验证
for checkpoint in .checkpoints/*.json; do
    if bash scripts/persistence/validate-checkpoint.sh "$checkpoint"; then
        echo "✅ $checkpoint valid"
    else
        echo "❌ $checkpoint invalid"
    fi
done
```

---

### cleanup-old-transactions.sh

**用途**: 清理旧事务

**用法**:
```bash
bash scripts/persistence/cleanup-old-transactions.sh [days]
```

**参数**:
- `days`: （可选）清理多少天前的事务，默认 30

**清理规则**:
- 只清理状态为 `completed` 或 `failed` 的事务
- 保留进行中的事务（`in_progress`）

**输出**:
```
Cleaning up transactions older than 30 days...
Deleting: docs/review-20260216-143022 (status: completed)
Deleting: .checkpoints/review-20260216-143022.json (status: completed)
Cleanup complete:
  - Deleted 1 data directories
  - Deleted 1 checkpoint files
```

**示例**:
```bash
# 清理 30 天前的事务
bash scripts/persistence/cleanup-old-transactions.sh 30

# 清理 7 天前的事务
bash scripts/persistence/cleanup-old-transactions.sh 7

# 查看会删除什么（dry-run）
# 编辑脚本，注释掉 rm 命令，仅打印
```

---

## 测试脚本

### 运行所有单元测试

```bash
cd /Users/mzdbxqh/source/component-creator-parent/claude-code-component-creator

# 单独运行每个测试
bash scripts/persistence/tests/test-init-transaction.sh
bash scripts/persistence/tests/test-save-load.sh
bash scripts/persistence/tests/test-checkpoint-update.sh
bash scripts/persistence/tests/test-validation.sh

# 运行性能基准测试
bash scripts/persistence/tests/benchmark.sh
```

**预期结果**:
- 所有单元测试通过（40/40）
- 性能基准符合目标（init <100ms, save <50ms, load <30ms, update <20ms）

---

## 库函数

### lib/common.sh

提供通用函数：

**check_dependencies()**: 检查依赖工具（jq）

**update_registry()**: 更新全局注册表

**validate_json()**: 验证 JSON 格式

**atomic_write()**: 原子写入文件

### lib/naming-rules.sh

提供命名规范函数：

**generate_filename()**: 根据文件类型生成文件名

**validate_transaction_id()**: 验证事务 ID 格式

---

## 使用示例

### 完整工作流示例

```bash
#!/bin/bash
set -euo pipefail

# 1. 初始化事务
TRANSACTION_ID="review-$(date +%Y%m%d-%H%M%S)"
bash scripts/persistence/init-transaction.sh review $TRANSACTION_ID review-aggregator

# 2. 保存初始配置
echo '{"components": ["cmd-review", "std-component-selection"]}' > /tmp/components.json
bash scripts/persistence/save-file.sh $TRANSACTION_ID components_list config /tmp/components.json

# 3. 更新进度
bash scripts/persistence/update-checkpoint.sh $TRANSACTION_ID 1 '{"scanned":16}'

# 4. 保存中间结果
echo '{"validated": true, "issues": []}' > /tmp/validated.json
bash scripts/persistence/save-file.sh $TRANSACTION_ID validated_results intermediate-result /tmp/validated.json

# 5. 更新进度
bash scripts/persistence/update-checkpoint.sh $TRANSACTION_ID 2 '{"validated":16}'

# 6. 加载数据
validated=$(bash scripts/persistence/load-file.sh $TRANSACTION_ID validated_results)
echo "$validated" | jq .

# 7. 完成事务
bash scripts/persistence/finalize-transaction.sh $TRANSACTION_ID completed

# 8. 验证 checkpoint
bash scripts/persistence/validate-checkpoint.sh .checkpoints/$TRANSACTION_ID.json
```

### 恢复流程示例

```bash
#!/bin/bash
set -euo pipefail

# 1. 检查未完成的事务
pending=$(bash scripts/persistence/list-transactions.sh review in_progress)

if [[ -n "$pending" ]]; then
    # 2. 提取最新的事务 ID
    TRANSACTION_ID=$(echo "$pending" | jq -r '.transaction_id' | tail -1)

    # 3. 加载 checkpoint
    checkpoint=$(cat .checkpoints/$TRANSACTION_ID.json)
    current_step=$(echo "$checkpoint" | jq -r '.current_step')

    echo "恢复事务: $TRANSACTION_ID"
    echo "从步骤 $((current_step + 1)) 继续"

    # 4. 加载之前保存的数据
    components=$(bash scripts/persistence/load-file.sh $TRANSACTION_ID components_list)

    # 5. 继续执行...
fi
```

---

## 故障排查

### 问题1: 脚本报错 "jq: command not found"

**原因**: 缺少 jq 依赖

**解决**:
```bash
# macOS
brew install jq

# Linux (Ubuntu/Debian)
sudo apt-get install jq

# Linux (CentOS/RHEL)
sudo yum install jq
```

### 问题2: checkpoint 更新失败 "Cannot acquire lock"

**原因**: 并发写入冲突或旧的锁文件未清理

**解决**:
```bash
# 1. 检查是否有其他进程正在使用
ps aux | grep persistence

# 2. 清理旧的锁文件（确保没有其他进程在运行）
rm -f .checkpoints/*.lock

# 3. 重新执行
```

### 问题3: load-file 报错 "key not found in checkpoint"

**原因**: checkpoint 中没有该 key 的记录

**解决**:
```bash
# 1. 查看可用的 keys
jq '.key_files | keys' .checkpoints/$TRANSACTION_ID.json

# 2. 检查文件是否已保存
ls -la docs/$TRANSACTION_ID/*/

# 3. 如果文件存在但 checkpoint 中没有记录，手动更新 checkpoint
jq '.key_files += {"your_key": "path/to/file.json"}' .checkpoints/$TRANSACTION_ID.json > /tmp/checkpoint.json
mv /tmp/checkpoint.json .checkpoints/$TRANSACTION_ID.json
```

### 问题4: 清理脚本删除了进行中的事务

**原因**: checkpoint 状态未正确更新

**解决**:
```bash
# 预防措施：使用 dry-run 模式（编辑脚本添加 --dry-run 参数）

# 恢复误删的文件（如果有 Git 备份）
git checkout docs/$TRANSACTION_ID/
git checkout .checkpoints/$TRANSACTION_ID.json
```

---

## 参考文档

- [用户指南](../../docs/long-task-persistence-user-guide.md)
- [迁移指南](../../docs/persistence-migration-guide.md)
- [设计规范](../../../docs/2026-03-16-long-task-persistence-standard-design.md)

---

**版本历史**:
- v3.2.0 (2026-03-16): 首次发布
