#!/bin/bash
# 完成事务（标记完成、清理临时文件）
#
# 用法: bash scripts/persistence/finalize-transaction.sh <transaction-id> <status>
# 示例: bash scripts/persistence/finalize-transaction.sh review-20260316-143022 completed

set -euo pipefail

# 检查参数
if [[ $# -lt 2 ]]; then
    echo "用法: $0 <transaction-id> <status>" >&2
    echo "" >&2
    echo "参数:" >&2
    echo "  status: completed | failed" >&2
    echo "" >&2
    echo "示例:" >&2
    echo "  $0 review-20260316-143022 completed" >&2
    exit 2
fi

TRANSACTION_ID=$1
STATUS=$2

# 验证 status
if [[ "$STATUS" != "completed" && "$STATUS" != "failed" ]]; then
    echo "Error: Invalid status: $STATUS (expected: completed or failed)" >&2
    exit 2
fi

# 导入库函数
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/lib/common.sh"

# 检查依赖
check_dependencies || exit 2

CHECKPOINT_FILE=".checkpoints/${TRANSACTION_ID}.json"

# 验证 checkpoint 存在
if [[ ! -f "$CHECKPOINT_FILE" ]]; then
    echo '{"status":"error","message":"Checkpoint not found: '"$CHECKPOINT_FILE"'"}' >&2
    exit 1
fi

# 读取数据目录
DATA_DIR=$(jq -r '.data_directory' "$CHECKPOINT_FILE")

# 清理临时文件
find "$DATA_DIR" -name "*.tmp.json" -delete 2>/dev/null || true

# 生成事务摘要
SUMMARY_FILE="${DATA_DIR}/transaction-summary.json"
jq --arg status "$STATUS" \
   --arg completed_at "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
   '{
     transaction_id,
     workflow_type,
     component_name,
     status: $status,
     created_at,
     completed_at: $completed_at,
     total_files: (.key_files | length),
     statistics
   }' \
   "$CHECKPOINT_FILE" > "$SUMMARY_FILE"

# 更新 checkpoint 状态
jq --arg status "$STATUS" \
   --arg completed_at "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
   '.status = $status | .completed_at = $completed_at | .last_updated = $completed_at' \
   "$CHECKPOINT_FILE" > "${CHECKPOINT_FILE}.tmp"
mv "${CHECKPOINT_FILE}.tmp" "$CHECKPOINT_FILE"

# 更新全局注册表
WORKFLOW_TYPE=$(jq -r '.workflow_type' "$CHECKPOINT_FILE")
update_registry "$TRANSACTION_ID" "$WORKFLOW_TYPE" "$STATUS"

# 输出结果
cat <<EOF
{
  "status": "success",
  "transaction_completed": true,
  "final_status": "$STATUS",
  "summary_file": "$SUMMARY_FILE"
}
EOF
