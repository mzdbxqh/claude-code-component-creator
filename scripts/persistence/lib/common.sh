#!/bin/bash
# 通用函数库

# 检查依赖工具
check_dependencies() {
    local missing_deps=()

    if ! command -v jq &> /dev/null; then
        missing_deps+=("jq")
    fi

    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        echo "Error: Missing required dependencies: ${missing_deps[*]}" >&2
        echo "Install: brew install ${missing_deps[*]} (macOS) or apt-get install ${missing_deps[*]} (Linux)" >&2
        return 1
    fi

    return 0
}

# 更新全局注册表
update_registry() {
    local transaction_id=$1
    local workflow_type=$2
    local status=$3

    if [[ -z "$transaction_id" || -z "$workflow_type" || -z "$status" ]]; then
        echo "Error: Missing required parameters" >&2
        return 1
    fi

    local registry_file=".checkpoints/registry.json"

    # 确保目录存在
    mkdir -p "$(dirname "$registry_file")"

    # 如果注册表不存在，创建
    if [[ ! -f "$registry_file" ]]; then
        echo '{"transactions":[]}' > "$registry_file"
    fi

    # 添加或更新事务记录 - 检测 jq 失败
    if ! jq --arg id "$transaction_id" \
       --arg type "$workflow_type" \
       --arg status "$status" \
       --arg updated "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
       '.transactions |= map(if .transaction_id == $id then .status = $status | .updated_at = $updated else . end) |
        if (.transactions | any(.transaction_id == $id)) then . else .transactions += [{transaction_id: $id, workflow_type: $type, status: $status, updated_at: $updated}] end' \
       "$registry_file" > "${registry_file}.tmp"; then
        rm -f "${registry_file}.tmp"
        echo "Error: Failed to update registry" >&2
        return 1
    fi

    mv "${registry_file}.tmp" "$registry_file"
}

# 验证 JSON 格式
validate_json() {
    local file=$1

    if [[ -z "$file" ]]; then
        echo "Error: File path is required" >&2
        return 1
    fi

    if [[ ! -f "$file" ]]; then
        echo "Error: File not found: $file" >&2
        return 1
    fi

    jq empty "$file" 2>/dev/null
}

# 原子写入文件（先写临时文件，再移动）
atomic_write() {
    local target_file=$1
    local content=$2

    if [[ -z "$target_file" ]]; then
        echo "Error: Target file path is required" >&2
        return 1
    fi

    # 确保父目录存在
    mkdir -p "$(dirname "$target_file")"

    echo "$content" > "${target_file}.tmp"
    mv "${target_file}.tmp" "$target_file"
}
