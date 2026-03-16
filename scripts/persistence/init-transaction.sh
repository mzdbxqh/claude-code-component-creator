#!/bin/bash
# 初始化事务
#
# 用法: bash scripts/persistence/init-transaction.sh <workflow-type> <transaction-id> [component-name]
# 示例: bash scripts/persistence/init-transaction.sh review review-20260316-143022 review-aggregator

set -euo pipefail

# 检查参数
if [[ $# -lt 2 ]]; then
    echo "用法: $0 <workflow-type> <transaction-id> [component-name]" >&2
    echo "" >&2
    echo "示例:" >&2
    echo "  $0 review review-20260316-143022 review-aggregator" >&2
    exit 2
fi

WORKFLOW_TYPE=$1
TRANSACTION_ID=$2
COMPONENT_NAME=${3:-${WORKFLOW_TYPE}}

# 导入库函数
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/lib/common.sh"
source "${SCRIPT_DIR}/lib/naming-rules.sh"

# 检查依赖
check_dependencies || exit 2

# 验证事务 ID 格式
validate_transaction_id "$TRANSACTION_ID" || exit 2

# 计算路径
DATA_DIR="docs/${TRANSACTION_ID}/${COMPONENT_NAME}"
CHECKPOINT_FILE=".checkpoints/${TRANSACTION_ID}.json"

# 检查事务是否已存在
if [[ -f "$CHECKPOINT_FILE" ]]; then
    echo '{"status":"error","message":"Transaction already exists: '"$TRANSACTION_ID"'"}' >&2
    exit 1
fi

# 创建目录
mkdir -p "$DATA_DIR"
mkdir -p ".checkpoints"

# 创建初始 checkpoint
cat > "$CHECKPOINT_FILE" <<EOF
{
  "version": "1.0",
  "transaction_id": "${TRANSACTION_ID}",
  "workflow_type": "${WORKFLOW_TYPE}",
  "component_name": "${COMPONENT_NAME}",
  "status": "in_progress",
  "current_step": 0,
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "last_updated": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "data_directory": "${DATA_DIR}",
  "key_files": {},
  "statistics": {}
}
EOF

# 更新全局注册表
update_registry "$TRANSACTION_ID" "$WORKFLOW_TYPE" "in_progress"

# 输出结果（JSON 格式，便于解析）
cat <<EOF
{
  "status": "success",
  "transaction_id": "${TRANSACTION_ID}",
  "data_dir": "${DATA_DIR}",
  "checkpoint_file": "${CHECKPOINT_FILE}"
}
EOF
