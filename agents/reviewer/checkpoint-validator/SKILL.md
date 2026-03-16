---
name: checkpoint-validator
description: 验证持久化 checkpoint 文件的完整性和一致性，确保恢复机制可用
model: haiku
tools:
  - Read
  - Grep
  - Glob
  - Write
---

# Checkpoint Validator - Checkpoint 验证器

## 用途

验证 CCC 持久化机制的 checkpoint 文件完整性和一致性，确保断点恢复机制可用。

**触发时机**:
- 长任务完成后验证 checkpoint
- 恢复前验证 checkpoint 可用性
- 定期检查 checkpoint 健康状态

**输出**: JSON 格式的验证报告，包含问题列表和修复建议

## Workflow

### Step 1: 扫描 checkpoint 文件

**操作**: 扫描所有 checkpoint 文件

```bash
checkpoint_files = Glob(".checkpoints/*.json")

# 排除注册表文件
checkpoint_files = [f for f in checkpoint_files if not f.endswith("registry.json")]
```

### Step 2: 对每个 checkpoint 执行验证

FOR each checkpoint_file IN checkpoint_files DO

#### 2.1 读取 checkpoint

```bash
checkpoint_data = Read(checkpoint_file)
checkpoint_json = json.loads(checkpoint_data)
```

#### 2.2 验证必需字段

检查以下必需字段是否存在：
- `transaction_id`
- `workflow_type`
- `status`
- `current_step`
- `data_directory`
- `key_files`

如果缺失，记录为 **ERROR**。

#### 2.3 验证数据目录存在

```bash
data_dir = checkpoint_json["data_directory"]

if not directory_exists(data_dir):
    记录 WARNING: "数据目录不存在: {data_dir}"
```

#### 2.4 验证引用的文件存在

```bash
for key, relative_path in checkpoint_json["key_files"].items():
    full_path = data_dir + "/" + relative_path
    
    if not file_exists(full_path):
        记录 WARNING: "引用的文件缺失: {key} -> {full_path}"
```

#### 2.5 验证状态一致性

```bash
# 如果状态为 completed 或 failed，应该有 completed_at
if checkpoint_json["status"] in ["completed", "failed"]:
    if "completed_at" not in checkpoint_json:
        记录 WARNING: "缺少完成时间戳"
```

#### 2.6 验证事务 ID 格式

```bash
transaction_id = checkpoint_json["transaction_id"]

# 格式: {workflow-type}-{YYYYMMDD}-{HHMMSS}
if not regex_match(transaction_id, "^[a-z]+-[0-9]{8}-[0-9]{6}$"):
    记录 ERROR: "事务 ID 格式无效: {transaction_id}"
```

END FOR

### Step 3: 生成验证报告

```bash
report = {
    "validation_timestamp": current_timestamp(),
    "checkpoints_scanned": len(checkpoint_files),
    "issues": [
        {
            "checkpoint": checkpoint_file,
            "severity": "ERROR/WARNING/INFO",
            "type": "missing_field/missing_file/invalid_format/...",
            "message": "详细说明",
            "fix_suggestion": "修复建议"
        },
        ...
    ],
    "summary": {
        "total_checkpoints": count,
        "healthy": count,
        "warnings": count,
        "errors": count
    }
}
```

### Step 4: 输出报告

```bash
# JSON 格式
Write("validation-report.json", json(report))

# Markdown 格式（可选）
Write("validation-report.md", markdown_report)
```

## 输出示例

```json
{
  "validation_timestamp": "2026-03-16T15:30:00Z",
  "checkpoints_scanned": 3,
  "issues": [
    {
      "checkpoint": ".checkpoints/review-20260316-143022.json",
      "severity": "WARNING",
      "type": "missing_file",
      "message": "引用的文件缺失: validated_results -> docs/.../validated-results.json",
      "fix_suggestion": "重新执行对应步骤或从备份恢复"
    },
    {
      "checkpoint": ".checkpoints/design-20260315-091500.json",
      "severity": "ERROR",
      "type": "missing_field",
      "message": "缺少必需字段: data_directory",
      "fix_suggestion": "使用 init-transaction.sh 重新创建 checkpoint"
    }
  ],
  "summary": {
    "total_checkpoints": 3,
    "healthy": 1,
    "warnings": 1,
    "errors": 1
  }
}
```

## 使用示例

```bash
# 在长任务组件中集成
Agent(ccc:reviewer:checkpoint-validator, checkpoint_file=".checkpoints/review-xxx.json")

# 验证所有 checkpoint
Agent(ccc:reviewer:checkpoint-validator)
```

## 错误处理

- 如果没有找到任何 checkpoint 文件，返回警告
- 如果 checkpoint JSON 格式无效，记录 ERROR 并继续验证其他文件
- 验证失败不应该中断主工作流，仅提供警告

## 修复建议

根据问题类型提供具体修复建议：

| 问题类型 | 修复建议 |
|---------|---------|
| missing_field | 使用 init-transaction.sh 重新创建标准 checkpoint |
| missing_file | 重新执行对应步骤，或从备份恢复 |
| invalid_format | 检查并修正 JSON 语法错误 |
| missing_directory | 创建缺失的数据目录 |
| status_inconsistency | 使用 finalize-transaction.sh 更新状态 |

## 集成示例

### 在 review-aggregator 中集成

在 Step 9（生成报告）之后：

```markdown
### Step 9.5: 验证 checkpoint（可选）

**操作**: 验证 checkpoint 完整性

```bash
validation_result = Agent(
    ccc:reviewer:checkpoint-validator,
    checkpoint_file=".checkpoints/${TRANSACTION_ID}.json"
)

# 如果发现问题，记录警告
if validation_result.summary.errors > 0:
    Write("checkpoint-validation-warnings.txt", validation_result.issues)
```
```

## 参考

- 设计文档: `docs/2026-03-16-long-task-persistence-standard-design.md`
- 反模式规则: `agents/reviewer/knowledge/antipatterns/persistence/PERSIST-004-checkpoint-metadata-incomplete.yaml`
- 验证脚本: `scripts/persistence/validate-checkpoint.sh`
