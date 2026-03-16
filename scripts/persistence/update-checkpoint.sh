#!/bin/bash
# 更新 checkpoint 的步骤和统计信息
#
# 用法: bash scripts/persistence/update-checkpoint.sh <transaction-id> <step> <stats-json>
# 示例: bash scripts/persistence/update-checkpoint.sh review-20260316-143022 5 '{"reviews_completed":16}'

set -euo pipefail

# 检查参数
if [[ $# -lt 3 ]]; then
    echo "用法: $0 <transaction-id> <step> <stats-json>" >&2
    echo "" >&2
    echo "示例:" >&2
    echo "  $0 review-20260316-143022 5 '{\"reviews_completed\":16}'" >&2
    exit 2
fi

TRANSACTION_ID=$1
STEP=$2
STATS_JSON=$3

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

# 验证 stats JSON 格式
echo "$STATS_JSON" | jq empty 2>/dev/null || {
    echo '{"status":"error","message":"Invalid JSON in stats parameter"}' >&2
    exit 2
}

# 使用文件锁确保并发安全
LOCK_FILE=".checkpoints/${TRANSACTION_ID}.lock"

# 尝试获取锁（最多等待5秒）
RETRY_COUNT=0
MAX_RETRIES=50
while [[ $RETRY_COUNT -lt $MAX_RETRIES ]]; do
    if mkdir "$LOCK_FILE" 2>/dev/null; then
        # 成功获取锁
        break
    fi
    # 等待100ms后重试
    sleep 0.1
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [[ $RETRY_COUNT -eq $MAX_RETRIES ]]; then
    echo '{"status":"error","message":"Cannot acquire lock on checkpoint"}' >&2
    exit 1
fi

# 更新 checkpoint
jq --argjson step "$STEP" \
   --argjson stats "$STATS_JSON" \
   '.current_step = $step |
    .statistics = (.statistics + $stats) |
    .last_updated = now |
    .last_updated |= todate' \
   "$CHECKPOINT_FILE" > "${CHECKPOINT_FILE}.tmp"
mv "${CHECKPOINT_FILE}.tmp" "$CHECKPOINT_FILE"

# 释放锁
rmdir "$LOCK_FILE"

# 输出结果
cat <<EOF
{
  "status": "success",
  "checkpoint_updated": true,
  "current_step": $STEP
}
EOF
