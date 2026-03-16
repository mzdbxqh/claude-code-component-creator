#!/bin/bash
# 验证 checkpoint 文件完整性
#
# 用法: bash scripts/persistence/validate-checkpoint.sh <checkpoint-file>
# 示例: bash scripts/persistence/validate-checkpoint.sh .checkpoints/review-xxx.json

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "用法: $0 <checkpoint-file>" >&2
    exit 2
fi

CHECKPOINT_FILE=$1

# 导入库函数
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/lib/common.sh"

# 检查依赖
check_dependencies || exit 2

# 验证文件存在
if [[ ! -f "$CHECKPOINT_FILE" ]]; then
    echo "Error: checkpoint file not found: $CHECKPOINT_FILE" >&2
    exit 1
fi

# 验证 JSON 格式
if ! validate_json "$CHECKPOINT_FILE"; then
    echo "Error: invalid JSON format" >&2
    exit 1
fi

# 验证必需字段
REQUIRED_FIELDS=(
    "transaction_id"
    "workflow_type"
    "status"
    "current_step"
    "data_directory"
    "key_files"
)

MISSING_FIELDS=()

for field in "${REQUIRED_FIELDS[@]}"; do
    if ! jq -e --arg f "$field" 'has($f)' "$CHECKPOINT_FILE" >/dev/null; then
        MISSING_FIELDS+=("$field")
    fi
done

if [[ ${#MISSING_FIELDS[@]} -gt 0 ]]; then
    echo "Error: missing required fields: ${MISSING_FIELDS[*]}" >&2
    exit 1
fi

# 验证文件存在性
DATA_DIR=$(jq -r '.data_directory' "$CHECKPOINT_FILE")
MISSING_FILES=()

for key in $(jq -r '.key_files | keys[]' "$CHECKPOINT_FILE"); do
    relative_path=$(jq -r --arg k "$key" '.key_files[$k]' "$CHECKPOINT_FILE")
    full_path="${DATA_DIR}/${relative_path}"

    if [[ ! -f "$full_path" ]]; then
        MISSING_FILES+=("$key:$full_path")
    fi
done

if [[ ${#MISSING_FILES[@]} -gt 0 ]]; then
    echo "Warning: missing files referenced in checkpoint:" >&2
    for item in "${MISSING_FILES[@]}"; do
        echo "  - $item" >&2
    done
fi

# 验证通过，输出摘要
echo "Checkpoint validation passed"
echo "Transaction: $(jq -r '.transaction_id' "$CHECKPOINT_FILE")"
echo "Status: $(jq -r '.status' "$CHECKPOINT_FILE")"
echo "Step: $(jq -r '.current_step' "$CHECKPOINT_FILE")"
echo "Files: $(jq -r '.key_files | length' "$CHECKPOINT_FILE")"
