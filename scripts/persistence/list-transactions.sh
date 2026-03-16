#!/bin/bash
# 列出所有事务
#
# 用法: bash scripts/persistence/list-transactions.sh [workflow-type] [status]
# 示例: bash scripts/persistence/list-transactions.sh review in_progress

set -euo pipefail

WORKFLOW_TYPE=${1:-""}
STATUS_FILTER=${2:-""}

# 导入库函数
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/lib/common.sh"

# 检查依赖
check_dependencies || exit 2

REGISTRY_FILE=".checkpoints/registry.json"

# 如果注册表不存在，返回空列表
if [[ ! -f "$REGISTRY_FILE" ]]; then
    echo '{"transactions":[]}'
    exit 0
fi

# 构建 jq 过滤器
JQ_FILTER=".transactions[]"

if [[ -n "$WORKFLOW_TYPE" ]]; then
    JQ_FILTER="$JQ_FILTER | select(.workflow_type == \"$WORKFLOW_TYPE\")"
fi

if [[ -n "$STATUS_FILTER" ]]; then
    JQ_FILTER="$JQ_FILTER | select(.status == \"$STATUS_FILTER\")"
fi

# 输出过滤后的事务
jq -c "$JQ_FILTER" "$REGISTRY_FILE" 2>/dev/null || echo ""
