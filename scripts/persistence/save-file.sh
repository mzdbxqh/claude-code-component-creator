#!/bin/bash
# 保存文件到事务目录
#
# 用法: bash scripts/persistence/save-file.sh <transaction-id> <key> <file-type> <content-file> [subdir]
# 示例: bash scripts/persistence/save-file.sh review-20260316-143022 components_list config /tmp/components.json

set -euo pipefail

# 检查参数
if [[ $# -lt 4 ]]; then
    echo "用法: $0 <transaction-id> <key> <file-type> <content-file> [subdir]" >&2
    echo "" >&2
    echo "示例:" >&2
    echo "  $0 review-20260316-143022 components_list config /tmp/components.json" >&2
    echo "  $0 review-20260316-143022 cmd-review intermediate-result /tmp/review.json review-results" >&2
    exit 2
fi

TRANSACTION_ID=$1
KEY=$2
FILE_TYPE=$3
CONTENT_FILE=$4
SUBDIR=${5:-""}

# 导入库函数
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/lib/common.sh"
source "${SCRIPT_DIR}/lib/naming-rules.sh"

# 检查依赖
check_dependencies || exit 2

# 验证内容文件存在
if [[ ! -f "$CONTENT_FILE" ]]; then
    echo '{"status":"error","message":"Content file not found: '"$CONTENT_FILE"'"}' >&2
    exit 2
fi

# 读取 checkpoint 获取 data_dir
CHECKPOINT_FILE=".checkpoints/${TRANSACTION_ID}.json"
if [[ ! -f "$CHECKPOINT_FILE" ]]; then
    echo '{"status":"error","message":"Checkpoint not found: '"$CHECKPOINT_FILE"'"}' >&2
    exit 1
fi

DATA_DIR=$(jq -r '.data_directory' "$CHECKPOINT_FILE")

# 根据 file_type 生成文件名
FILENAME=$(generate_filename "$KEY" "$FILE_TYPE")

# 计算完整路径
if [[ -n "$SUBDIR" ]]; then
    TARGET_DIR="${DATA_DIR}/${SUBDIR}"
    mkdir -p "$TARGET_DIR"
    TARGET_PATH="${TARGET_DIR}/${FILENAME}"
    RELATIVE_PATH="${SUBDIR}/${FILENAME}"
else
    TARGET_PATH="${DATA_DIR}/${FILENAME}"
    RELATIVE_PATH="${FILENAME}"
fi

# 复制文件
cp "$CONTENT_FILE" "$TARGET_PATH"

# 更新 checkpoint (使用文件锁确保并发安全)
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
jq --arg key "$KEY" --arg path "$RELATIVE_PATH" \
   '.key_files[$key] = $path | .last_updated = now | .last_updated |= todate' \
   "$CHECKPOINT_FILE" > "${CHECKPOINT_FILE}.tmp"
mv "${CHECKPOINT_FILE}.tmp" "$CHECKPOINT_FILE"

# 释放锁
rmdir "$LOCK_FILE"

# 输出结果
cat <<EOF
{
  "status": "success",
  "file_path": "${TARGET_PATH}",
  "relative_path": "${RELATIVE_PATH}"
}
EOF
