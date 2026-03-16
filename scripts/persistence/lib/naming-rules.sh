#!/bin/bash
# 文件命名规范

# 根据文件类型生成文件名
generate_filename() {
    local key=$1
    local file_type=$2

    if [[ -z "$key" || -z "$file_type" ]]; then
        echo "Error: Missing required parameters (key, file_type)" >&2
        return 1
    fi

    local date_prefix=$(date +%Y-%m-%d)

    case "$file_type" in
        config)
            echo "${key}.json"
            ;;
        intermediate-result)
            echo "${key}-results.json"
            ;;
        final-report)
            echo "${date_prefix}-${key}.md"
            ;;
        temp)
            echo "${key}.tmp.json"
            ;;
        *)
            echo "${key}.json"
            ;;
    esac
}

# 验证事务 ID 格式
validate_transaction_id() {
    local transaction_id=$1

    if [[ -z "$transaction_id" ]]; then
        echo "Error: Transaction ID is required" >&2
        return 1
    fi

    # 格式: {workflow-type}-{YYYYMMDD}-{HHMMSS}
    if [[ ! "$transaction_id" =~ ^[a-z]+-[0-9]{8}-[0-9]{6}$ ]]; then
        echo "Error: Invalid transaction ID format: $transaction_id" >&2
        echo "Expected format: {workflow-type}-{YYYYMMDD}-{HHMMSS}" >&2
        echo "Example: review-20260316-143022" >&2
        return 1
    fi

    return 0
}
