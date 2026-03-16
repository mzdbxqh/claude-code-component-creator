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

    local registry_file=".checkpoints/registry.json"

    # 如果注册表不存在，创建
    if [[ ! -f "$registry_file" ]]; then
        echo '{"transactions":[]}' > "$registry_file"
    fi

    # 添加或更新事务记录
    jq --arg id "$transaction_id" \
       --arg type "$workflow_type" \
       --arg status "$status" \
       --arg updated "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
       '.transactions |= map(if .transaction_id == $id then .status = $status | .updated_at = $updated else . end) |
        if any(.transaction_id == $id) then . else .transactions += [{transaction_id: $id, workflow_type: $type, status: $status, updated_at: $updated}] end' \
       "$registry_file" > "${registry_file}.tmp"
    mv "${registry_file}.tmp" "$registry_file"
}

# 验证 JSON 格式
validate_json() {
    local file=$1
    jq empty "$file" 2>/dev/null
}

# 原子写入文件（先写临时文件，再移动）
atomic_write() {
    local target_file=$1
    local content=$2

    echo "$content" > "${target_file}.tmp"
    mv "${target_file}.tmp" "$target_file"
}
