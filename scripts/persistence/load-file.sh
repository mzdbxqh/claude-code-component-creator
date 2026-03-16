#!/bin/bash
# 从事务加载文件
#
# 用法: bash scripts/persistence/load-file.sh <transaction-id> <key>
# 示例: bash scripts/persistence/load-file.sh review-20260316-143022 components_list

set -euo pipefail

# 检查参数
if [[ $# -lt 2 ]]; then
    echo "用法: $0 <transaction-id> <key>" >&2
    echo "" >&2
    echo "示例:" >&2
    echo "  $0 review-20260316-143022 components_list" >&2
    exit 2
fi

TRANSACTION_ID=$1
KEY=$2

# 导入库函数
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/lib/common.sh"

# 检查依赖
check_dependencies || exit 2

CHECKPOINT_FILE=".checkpoints/${TRANSACTION_ID}.json"

# 验证 checkpoint 存在
if [[ ! -f "$CHECKPOINT_FILE" ]]; then
    echo "Error: checkpoint not found: $CHECKPOINT_FILE" >&2
    exit 1
fi

# 从 checkpoint 获取文件路径
RELATIVE_PATH=$(jq -r --arg key "$KEY" '.key_files[$key] // empty' "$CHECKPOINT_FILE")

if [[ -z "$RELATIVE_PATH" ]]; then
    echo "Error: key '$KEY' not found in checkpoint" >&2
    echo "Available keys:" >&2
    jq -r '.key_files | keys[]' "$CHECKPOINT_FILE" >&2
    exit 1
fi

DATA_DIR=$(jq -r '.data_directory' "$CHECKPOINT_FILE")
FILE_PATH="${DATA_DIR}/${RELATIVE_PATH}"

# 验证文件存在
if [[ ! -f "$FILE_PATH" ]]; then
    echo "Error: file not found: $FILE_PATH" >&2
    exit 1
fi

# 输出文件内容到 stdout（便于捕获）
cat "$FILE_PATH"
