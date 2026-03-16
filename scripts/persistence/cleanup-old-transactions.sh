#!/bin/bash
# 清理旧事务
#
# 用法: bash scripts/persistence/cleanup-old-transactions.sh [days]
# 示例: bash scripts/persistence/cleanup-old-transactions.sh 30

set -euo pipefail

DAYS=${1:-30}

echo "Cleaning up transactions older than $DAYS days..."

# 清理旧的数据目录（已完成的事务）
deleted_dirs=0
if [[ -d "docs" ]]; then
    while IFS= read -r dir; do
        # 检查对应的 checkpoint 是否为 completed 或 failed
        dir_name=$(basename "$dir")
        checkpoint_file=".checkpoints/${dir_name}.json"

        if [[ -f "$checkpoint_file" ]]; then
            status=$(jq -r '.status' "$checkpoint_file" 2>/dev/null || echo "unknown")
            if [[ "$status" == "completed" || "$status" == "failed" ]]; then
                echo "Deleting: $dir (status: $status)"
                rm -rf "$dir"
                ((deleted_dirs++))
            fi
        fi
    done < <(find docs -mindepth 1 -maxdepth 1 -type d -mtime "+$DAYS" 2>/dev/null || true)
fi

# 清理旧的 checkpoint 文件（已完成的事务）
deleted_checkpoints=0
if [[ -d ".checkpoints" ]]; then
    while IFS= read -r checkpoint; do
        if [[ -f "$checkpoint" ]]; then
            status=$(jq -r '.status' "$checkpoint" 2>/dev/null || echo "unknown")
            if [[ "$status" == "completed" || "$status" == "failed" ]]; then
                echo "Deleting: $checkpoint (status: $status)"
                rm -f "$checkpoint"
                ((deleted_checkpoints++))
            fi
        fi
    done < <(find .checkpoints -name "*.json" -mtime "+$DAYS" ! -name "registry.json" 2>/dev/null || true)
fi

echo "Cleanup complete:"
echo "  - Deleted $deleted_dirs data directories"
echo "  - Deleted $deleted_checkpoints checkpoint files"
